"""Local equipment reservation system."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


ROOT = Path(__file__).resolve().parent
INVENTORY_PATH = ROOT / "inventory.json"
DEFAULT_DATA_PATH = ROOT / "data" / "reservations.json"
DATE_FORMAT = "%Y-%m-%dT%H:%M"


class ReservationError(ValueError):
    """A reservation request violates a business rule."""


@dataclass(frozen=True)
class Unit:
    id: str
    name: str


@dataclass
class Reservation:
    id: str
    unit_id: str
    equipment: str
    requester: str
    start: datetime
    end: datetime
    status: str = "active"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Reservation:
        reservation = cls(
            id=str(data["id"]),
            unit_id=str(data["unit_id"]),
            equipment=str(data["equipment"]),
            requester=str(data["requester"]),
            start=datetime.fromisoformat(data["start"]),
            end=datetime.fromisoformat(data["end"]),
            status=str(data["status"]),
        )
        if reservation.status not in {"active", "cancelled"}:
            raise ValueError(f"Estado inválido en el archivo de datos: {reservation.status}")
        if reservation.start.tzinfo is not None or reservation.end.tzinfo is not None:
            raise ValueError("Las fechas guardadas deben usar hora local sin zona horaria.")
        if reservation.start >= reservation.end:
            raise ValueError("Una reserva guardada tiene un intervalo inválido.")
        return reservation

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "equipment": self.equipment,
            "requester": self.requester,
            "start": self.start.isoformat(timespec="minutes"),
            "end": self.end.isoformat(timespec="minutes"),
            "status": self.status,
        }


def load_inventory(path: Path = INVENTORY_PATH) -> dict[str, Unit]:
    with path.open(encoding="utf-8") as inventory_file:
        items = json.load(inventory_file)

    if not isinstance(items, list):
        raise ValueError("El inventario debe ser una lista de unidades.")

    inventory: dict[str, Unit] = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("id") or not item.get("name"):
            raise ValueError("Cada unidad debe tener un ID y un nombre.")
        unit = Unit(id=str(item["id"]), name=str(item["name"]))
        if unit.id in inventory:
            raise ValueError(f"ID de unidad duplicado en el inventario: {unit.id}")
        inventory[unit.id] = unit
    return inventory


class ReservationService:
    def __init__(self, inventory: dict[str, Unit], data_path: Path) -> None:
        self.inventory = inventory
        self.data_path = data_path
        self.reservations = self._load_reservations()

    def _load_reservations(self) -> list[Reservation]:
        if not self.data_path.exists():
            return []
        with self.data_path.open(encoding="utf-8") as data_file:
            records = json.load(data_file)
        if not isinstance(records, list):
            raise ValueError("El archivo de reservas debe contener una lista.")
        return [Reservation.from_dict(record) for record in records]

    def _save_reservations(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path: Path | None = None
        try:
            with NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.data_path.parent,
                prefix=f".{self.data_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)
                json.dump(
                    [reservation.to_dict() for reservation in self.reservations],
                    temp_file,
                    ensure_ascii=False,
                    indent=2,
                )
                temp_file.write("\n")
            os.replace(temp_path, self.data_path)
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink()

    @staticmethod
    def _validate_interval(start: datetime, end: datetime) -> None:
        if start.tzinfo is not None or end.tzinfo is not None:
            raise ReservationError("Usa fechas sin zona horaria, en hora local.")
        if start >= end:
            raise ReservationError("El inicio debe ser anterior al fin.")

    def _has_conflict(self, unit_id: str, start: datetime, end: datetime) -> bool:
        return any(
            reservation.status == "active"
            and reservation.unit_id == unit_id
            and start < reservation.end
            and reservation.start < end
            for reservation in self.reservations
        )

    def available_units(self, start: datetime, end: datetime) -> list[Unit]:
        self._validate_interval(start, end)
        return [
            unit
            for unit in self.inventory.values()
            if not self._has_conflict(unit.id, start, end)
        ]

    def create(
        self, unit_id: str, requester: str, start: datetime, end: datetime
    ) -> Reservation:
        self._validate_interval(start, end)
        if unit_id not in self.inventory:
            raise ReservationError(f"Unidad desconocida: {unit_id}")
        if not requester.strip():
            raise ReservationError("El solicitante no puede estar vacío.")
        if self._has_conflict(unit_id, start, end):
            raise ReservationError("La unidad ya tiene una reserva activa superpuesta.")

        unit = self.inventory[unit_id]
        reservation = Reservation(
            id=f"res_{uuid.uuid4().hex[:12]}",
            unit_id=unit.id,
            equipment=unit.name,
            requester=requester.strip(),
            start=start,
            end=end,
        )
        self.reservations.append(reservation)
        self._save_reservations()
        return reservation

    def cancel(self, reservation_id: str) -> Reservation:
        reservation = next(
            (item for item in self.reservations if item.id == reservation_id),
            None,
        )
        if reservation is None:
            raise ReservationError(f"No existe la reserva {reservation_id}.")
        if reservation.status == "cancelled":
            raise ReservationError(f"La reserva {reservation_id} ya está cancelada.")
        reservation.status = "cancelled"
        self._save_reservations()
        return reservation


def parse_datetime(value: str) -> datetime:
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"Fecha inválida: {value!r}. Usa AAAA-MM-DDTHH:MM, por ejemplo 2030-04-15T10:00."
        ) from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reservas locales de equipos de laboratorio.")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help=f"Archivo JSON de reservas (por defecto: {DEFAULT_DATA_PATH})",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("list", help="Mostrar todas las reservas.")

    availability = commands.add_parser("availability", help="Consultar unidades disponibles.")
    availability.add_argument("--start", required=True, type=parse_datetime)
    availability.add_argument("--end", required=True, type=parse_datetime)

    reserve = commands.add_parser("reserve", help="Crear una reserva.")
    reserve.add_argument("--unit", required=True)
    reserve.add_argument("--requester", required=True)
    reserve.add_argument("--start", required=True, type=parse_datetime)
    reserve.add_argument("--end", required=True, type=parse_datetime)

    cancel = commands.add_parser("cancel", help="Cancelar una reserva por ID.")
    cancel.add_argument("--id", required=True)
    return parser


def format_reservation(reservation: Reservation) -> str:
    return (
        f"{reservation.id} | {reservation.unit_id} ({reservation.equipment}) | "
        f"{reservation.requester} | "
        f"{reservation.start.strftime(DATE_FORMAT)} a {reservation.end.strftime(DATE_FORMAT)} | "
        f"{reservation.status}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        service = ReservationService(load_inventory(), args.data_file)
        if args.command == "list":
            if not service.reservations:
                print("No hay reservas.")
            for reservation in service.reservations:
                print(format_reservation(reservation))
        elif args.command == "availability":
            units = service.available_units(args.start, args.end)
            if not units:
                print("No hay unidades disponibles para ese intervalo.")
            for unit in units:
                print(f"{unit.id} | {unit.name}")
        elif args.command == "reserve":
            reservation = service.create(
                args.unit, args.requester, args.start, args.end
            )
            print(f"Reserva creada: {format_reservation(reservation)}")
        elif args.command == "cancel":
            reservation = service.cancel(args.id)
            print(f"Reserva cancelada: {format_reservation(reservation)}")
    except (ReservationError, OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
