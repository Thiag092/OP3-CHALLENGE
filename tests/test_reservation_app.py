import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from reservation_app import ReservationError, ReservationService, Unit


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2030, 4, 15, hour, minute)


class ReservationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = Path(self.temp_dir.name) / "reservations.json"
        self.inventory = {
            "MIC-01": Unit("MIC-01", "Microscopio digital"),
            "MIC-02": Unit("MIC-02", "Microscopio digital"),
        }
        self.service = ReservationService(self.inventory, self.data_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_creates_valid_reservation(self) -> None:
        reservation = self.service.create("MIC-01", "Ana", at(10), at(11))

        self.assertEqual(reservation.unit_id, "MIC-01")
        self.assertEqual(reservation.requester, "Ana")
        self.assertEqual(reservation.status, "active")

    def test_rejects_overlapping_active_reservation(self) -> None:
        self.service.create("MIC-01", "Ana", at(10), at(11))

        with self.assertRaises(ReservationError):
            self.service.create("MIC-01", "Luis", at(10, 30), at(11, 30))

    def test_allows_consecutive_reservations(self) -> None:
        self.service.create("MIC-01", "Ana", at(10), at(11))

        next_reservation = self.service.create("MIC-01", "Luis", at(11), at(12))

        self.assertEqual(next_reservation.start, at(11))

    def test_allows_same_time_on_different_units(self) -> None:
        first = self.service.create("MIC-01", "Ana", at(10), at(11))

        second = self.service.create("MIC-02", "Luis", at(10), at(11))

        self.assertNotEqual(first.unit_id, second.unit_id)

    def test_availability_uses_the_same_interval_rules(self) -> None:
        self.service.create("MIC-01", "Ana", at(10), at(11))

        overlapping = self.service.available_units(at(10, 30), at(11, 30))
        consecutive = self.service.available_units(at(11), at(12))

        self.assertNotIn("MIC-01", {unit.id for unit in overlapping})
        self.assertIn("MIC-01", {unit.id for unit in consecutive})

    def test_rejects_unknown_unit_and_blank_requester(self) -> None:
        with self.assertRaises(ReservationError):
            self.service.create("NO-EXISTE", "Ana", at(10), at(11))
        with self.assertRaises(ReservationError):
            self.service.create("MIC-01", "   ", at(10), at(11))

    def test_rejects_invalid_interval(self) -> None:
        with self.assertRaises(ReservationError):
            self.service.create("MIC-01", "Ana", at(11), at(10))
        with self.assertRaises(ReservationError):
            self.service.create("MIC-01", "Ana", at(10), at(10))

    def test_cancel_keeps_record_and_releases_interval(self) -> None:
        original = self.service.create("MIC-01", "Ana", at(10), at(11))

        cancelled = self.service.cancel(original.id)
        replacement = self.service.create("MIC-01", "Luis", at(10), at(11))

        self.assertEqual(cancelled.id, original.id)
        self.assertEqual(cancelled.status, "cancelled")
        self.assertIn(cancelled, self.service.reservations)
        self.assertNotEqual(replacement.id, original.id)

    def test_active_and_cancelled_records_survive_restart(self) -> None:
        cancelled = self.service.create("MIC-01", "Ana", at(10), at(11))
        active = self.service.create("MIC-02", "Luis", at(10), at(11))
        self.service.cancel(cancelled.id)

        restarted = ReservationService(self.inventory, self.data_path)

        by_id = {reservation.id: reservation for reservation in restarted.reservations}
        self.assertEqual(by_id[cancelled.id].status, "cancelled")
        self.assertEqual(by_id[active.id].status, "active")
        stored = json.loads(self.data_path.read_text(encoding="utf-8"))
        self.assertEqual(len(stored), 2)


if __name__ == "__main__":
    unittest.main()
