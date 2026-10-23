# Instrucciones para el agente

- Mantén el inventario fijo en `inventory.json`; no agregues operaciones para crear o editar unidades.
- Trata las reservas como intervalos semiabiertos `[inicio, fin)`: dos reservas de la misma unidad pueden ser consecutivas, pero no superponerse.
- Usa exactamente la misma regla de disponibilidad para consultar y crear reservas; las canceladas no bloquean el horario.
- Conserva cada reserva cancelada con el mismo ID y sus datos originales.
- Persiste cambios en JSON local y no agregues dependencias externas salvo que sean necesarias y se justifiquen.
- Antes de finalizar, ejecuta `python -m unittest discover -s tests -v` y comunica el resultado real. No afirmes que una prueba pasó si no se ejecutó.
- No inventes episodios, resultados, correcciones ni datos del entorno. Registra evidencia solo después de que ocurra.
