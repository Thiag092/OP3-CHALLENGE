# Sistema local de reservas de equipos

Aplicación de consola para consultar disponibilidad, reservar una unidad del inventario y cancelar una reserva sin borrar su historial. Está implementada con Python y la biblioteca estándar; no necesita servicios externos ni una cuenta de modelo para ejecutarse.

## Especificación breve

**Problema y alcance.** La coordinación del laboratorio necesita evitar reservas duplicadas, consultar disponibilidad y liberar horarios cancelados. El inventario es fijo y cada ID identifica una unidad física.

**Requisitos verificables.**

- Consultar disponibilidad por intervalo.
- Crear una reserva con unidad conocida, solicitante no vacío, inicio y fin válidos e inicio anterior al fin.
- Rechazar superposiciones activas de una misma unidad.
- Permitir intervalos consecutivos y reservas simultáneas de unidades diferentes.
- Cancelar sin borrar el identificador ni los datos; una cancelación libera el intervalo.
- Recuperar reservas activas y canceladas al reiniciar.

**Reglas y supuestos.** Los intervalos son semiabiertos `[inicio, fin)`, por eso una reserva que termina a las 11:00 no se superpone con otra que empieza a las 11:00. Las fechas usan hora local sin zona horaria y el formato `AAAA-MM-DDTHH:MM`. No se rechazan fechas pasadas ni se imponen límites de duración o anticipación: la consigna no los especifica. Los nombres de solicitantes de ejemplo son ficticios.

**Criterios de aceptación.** Las pruebas automatizadas cubren creación válida, superposición, límites consecutivos, unidades distintas, entradas inválidas, cancelación, liberación del horario y persistencia tras reiniciar.

## Solución

**Estructura y carga inicial:** `reservation_app.py` contiene la lógica y los comandos de consola; `inventory.json` contiene las cinco unidades iniciales y se lee al iniciar cada comando; `tests/` contiene pruebas con `unittest`; `data/reservations.json` se crea al guardar la primera reserva. El inventario es fijo; no hay comandos para agregar, modificar ni eliminar unidades.

**Requisitos y versión:** Python 3.10 o posterior. No hay dependencias de terceros ni pasos de instalación. El archivo de reservas se guarda por defecto en `data/reservations.json`. Las escrituras reemplazan el archivo mediante un temporal en el mismo directorio. No borres ese archivo para reiniciar la aplicación: contiene el historial. No hay un comando de reinicio destructivo; para una prueba limpia, pasa otro `--data-file` temporal.

**Instalación y ejecución** (desde la raíz del proyecto):

```powershell
python --version
python -m unittest discover -s tests -v
python reservation_app.py list
python reservation_app.py availability --start 2030-04-15T10:00 --end 2030-04-15T11:00
python reservation_app.py reserve --unit MIC-01 --requester "Ana" --start 2030-04-15T10:00 --end 2030-04-15T11:00
python reservation_app.py list
python reservation_app.py cancel --id ID_QUE_MUESTRA_LA_RESERVA
```

Ejemplo de disponibilidad: si `MIC-01` está reservado de 10:00 a 11:00, otra solicitud de 10:30 a 11:30 se rechaza y una de 11:00 a 12:00 se permite. `MIC-02` puede reservarse de 10:00 a 11:00 al mismo tiempo.

Salida real de la prueba de consola registrada en [evidence/episodio-3-cli-smoke.txt](./evidence/episodio-3-cli-smoke.txt):

```text
Reserva cancelada: res_868123f2572a | MIC-01 (Microscopio digital) | Prueba ficticia | 2030-04-15T10:00 a 2030-04-15T11:00 | cancelled
res_868123f2572a | MIC-01 (Microscopio digital) | Prueba ficticia | 2030-04-15T10:00 a 2030-04-15T11:00 | cancelled
res_3743c69cbc12 | MIC-01 (Microscopio digital) | Prueba consecutiva | 2030-04-15T11:00 a 2030-04-15T12:00 | active
```


## Preparación del agente

**Entorno y modelo:** agente de programación en VS Code con Copilot SDK, actuando sobre los archivos del espacio de trabajo. El identificador y la versión del modelo no fueron visibles. Se eligió este entorno porque la consigna pide que el agente trabaje sobre un repositorio con herramientas reales.

**Instrucciones, contexto y permisos:** `.github/copilot-instructions.md` fija reglas específicas de intervalos consecutivos, disponibilidad, cancelación, persistencia y reporte honesto de pruebas. El contexto de requisitos es `challenge-agents.pdf`; también se revisaron el código, las pruebas y el inventario. Se excluyeron credenciales, datos personales reales y servicios externos. Para las verificaciones documentadas aquí se usaron Python y comandos locales; la prueba manual escribió en un JSON temporal y no modificó el inventario ni el archivo de reservas predeterminado. El texto exacto de la instrucción original de construcción no quedó preservado, por lo que no se presenta como cita literal.

**Controles, adaptación y retención del progreso:** se revisaron la implementación y las pruebas antes de informar resultados; no se aceptaron cambios de lógica porque la revisión de disponibilidad no encontró una discrepancia. La adaptación verificable es modelar intervalos como `[inicio, fin)`, aplicada en `ReservationService._has_conflict` y comprobada por `test_allows_consecutive_reservations` y `test_availability_uses_the_same_interval_rules`. Las decisiones y resultados se conservan en este README y en la evidencia versionada; los comandos y resultados de persistencia están en `evidence/episodio-3-cli-smoke.txt`.

## Registro de episodios, decisiones y delegación
**Prompt Original:**:

*Necesito adaptar este proyecto para hacer un sistema de reservas de equipos de laboratorio usando TypeScript, Bun y SQLite.*

*El sistema tiene que manejar este inventario:*

- *MIC-01: Microscopio digital*
- *MIC-02: Microscopio digital*
- *OSC-01: Osciloscopio*
- *MUL-01: Multímetro*
- *FUE-01: Fuente de alimentación*

*Quiero poder consultar si un equipo está disponible, crear una reserva y cancelarla. Cada reserva tiene que guardar un ID, el equipo, el nombre del solicitante, fecha y hora de inicio y fin, y su estado.*
*No se pueden aceptar reservas superpuestas para el mismo equipo, pero sí horarios consecutivos. Por ejemplo, si MIC-01 está reservado de 10:00 a 11:00, no se puede reservar de 10:30 a 11:30, pero sí de 11:00 a 12:00. Equipos diferentes pueden reservarse al mismo tiempo.*

*Cuando se cancela una reserva no quiero que se elimine, sino que quede guardada como cancelada y que ese horario vuelva a estar disponible.*

*Los datos tienen que persistir en SQLite aunque cierre y vuelva a ejecutar la aplicación.*

*También necesito pruebas automáticas para comprobar reservas válidas, superposiciones, horarios consecutivos, equipos distintos al mismo tiempo, datos inválidos, cancelaciones y persistencia.*

*Primero revisá cómo está armado el proyecto actual y tratá de reutilizar su estructura. Después hacé los cambios necesarios de forma progresiva y explicame qué archivos vas modificando y por qué. Ejecutá las pruebas para comprobar que realmente funciona.*

*Por último, ayudame a dejar un README donde se explique cómo ejecutar el proyecto, cómo correr las pruebas, las decisiones que tomamos y el uso que hice del agente durante el desarrollo.*
##
### Episodio 1 — Base funcional

- **Objetivo y requisito:** generar una base ejecutable del sistema local de reservas, con consola y almacenamiento JSON.
- **Contexto e instrucción:** el registro inicial del proyecto atribuye la tarea a la consigna oficial y a la selección de Python. 
- **Acción / resultado:** la aplicación, el inventario inicial y las pruebas están en el commit `f0dcc85` y en `reservation_app.py`, `inventory.json` y `tests/test_reservation_app.py`.
- **Revisión del agente:** la suite actual y la verificación de persistencia registradas en este README comprueban el comportamiento principal.

- **Evidencia:** los archivos listados arriba y el historial Git del repositorio.

### Episodio 2 — Revisar disponibilidad y límites de intervalos



**Acción y resultado observado:** se inspeccionaron `ReservationService._has_conflict`, `available_units` y `create`. Ambas operaciones usan la misma detección de conflicto: solo cuenta reservas activas de la misma unidad y usa `inicio_nuevo < fin_existente` junto con `inicio_existente < fin_nuevo`. No se detectó una carencia, así que no se modificó código ni se necesitó agregar una prueba. `inventory.json` no se modificó.

**Pruebas ejecutadas:** cuatro pruebas enfocadas pasaron: `test_availability_uses_the_same_interval_rules`, `test_rejects_overlapping_active_reservation`, `test_allows_consecutive_reservations` y `test_allows_same_time_on_different_units`. Después, `python -m unittest discover -s tests -v` ejecutó la suite completa: 9 pruebas pasaron. Entorno observado: Python 3.13.14. `git diff --check` no reportó errores.



**Evidencia:** las pruebas están definidas en `tests/test_reservation_app.py`. Los comandos se ejecutaron en la terminal durante esta sesión; no se guardó una transcripción de terminal aparte.

### Episodio 3 — Comprobar cancelación y persistencia entre ejecuciones


- **Contexto e instrucción:** Se ejecutó el procedimiento CLI con `--data-file` temporal, solicitantes ficticios y sin modificar `inventory.json` ni el archivo de datos habitual.
- **Acción / resultado observado:** cada comando se ejecutó en un proceso nuevo. La reserva superpuesta fue rechazada con código 1; la consecutiva se creó; la primera reserva mantuvo su ID y apareció como `cancelled`; la consecutiva siguió `active`; disponibilidad volvió a incluir `MIC-01` para el horario liberado.
- **Decisión humana:** la salida registrada confirma persistencia entre procesos, conservación de la cancelación y liberación del intervalo.
- **Evidencia:** salida completa, versión de Python y códigos de salida en [evidence/episodio-3-cli-smoke.txt](./evidence/episodio-3-cli-smoke.txt).

### Resultados de verificación

 El archivo de evidencia registra el procedimiento manual reproducible y sus resultados observados.

| Comando o procedimiento | Versión de Python | Resultado observado |
| --- | --- | --- |
| Cuatro pruebas enfocadas de disponibilidad, superposición, consecutivas y unidades distintas | 3.13.14 | 4 pruebas pasaron |
| Prueba CLI con `--data-file` temporal; reservas, consultas, cancelación y `list` en procesos nuevos | 3.13.14 | Rechazó superposición (código 1), permitió la consecutiva, conservó la reserva cancelada y la activa y liberó el intervalo; evidencia en `evidence/episodio-3-cli-smoke.txt` |
| `python -m unittest discover -s tests -v` | 3.13.14 | 9 pruebas pasaron tras actualizar la documentación |
