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

**Estructura:** `reservation_app.py` contiene la lógica y los comandos de consola; `inventory.json` contiene las cinco unidades iniciales; `tests/` contiene pruebas con `unittest`; `data/reservations.json` se crea al guardar la primera reserva.

**Requisitos y versión:** Python 3.10 o posterior. No hay dependencias de terceros. El inventario se lee junto al programa; el archivo de reservas se guarda por defecto en `data/reservations.json`. Las escrituras reemplazan el archivo mediante un temporal en el mismo directorio. No borres ese archivo para reiniciar la aplicación: contiene el historial. Para probar desde cero, pasa otro `--data-file` temporal.

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

**Pendientes y límites:** es una aplicación local para un único proceso; no implementa usuarios reales, roles, interfaz gráfica ni concurrencia distribuida.

## Preparación del agente

**Entorno:** agente de programación en VS Code con Copilot SDK, actuando sobre los archivos del espacio de trabajo. El identificador y la versión del modelo no fueron visibles en esta sesión, así que no se inventan. Se eligió este entorno porque la consigna pide que el agente trabaje sobre un repositorio con herramientas reales.

**Instrucciones y contexto:** `.github/copilot-instructions.md` fija reglas específicas de intervalos consecutivos, disponibilidad, cancelación, persistencia y reporte honesto de pruebas. El contexto fue la consigna `challenge-agents.pdf`; se excluyeron credenciales, datos personales reales y servicios externos.

**Herramientas, controles y adaptación:** el agente leyó la consigna, creó archivos en el espacio de trabajo y ejecutó pruebas locales. La adaptación verificable es la instrucción de modelar intervalos como `[inicio, fin)`, aplicada en `ReservationService._has_conflict` y comprobada por `test_allows_consecutive_reservations`. 

## Registro de decisiones y delegación

Registra aquí solo episodios que hayan ocurrido. No pegues conversaciones privadas completas ni inventes fallas, resultados o decisiones. Enlaza los archivos y resultados de la versión que se entrega.

### Episodio 1 — Base funcional

- **Objetivo y requisito:** generar una base ejecutable del sistema local de reservas, con consola y almacenamiento JSON.
- **Contexto e instrucción:** la consigna del PDF y la selección del usuario de crear la base en Python. Se aplicaron las instrucciones de `.github/copilot-instructions.md`.
- **Acción / resultado del agente:** se crearon la aplicación, el inventario inicial, las pruebas y esta documentación.
- **Decisión humana:** pendiente de revisión de la persona que entrega; no se afirma aceptación.
- **Evidencia:** `reservation_app.py`, `inventory.json`, `tests/test_reservation_app.py` y el resultado de `python -m unittest discover -s tests -v` que se debe registrar abajo tras ejecutarlo.

### Registro de episodios 2 y 3

El episodio 2 se realizó en esta sesión y se documenta abajo. El episodio 3 sigue pendiente; no se afirma que se haya ejecutado.

#### Episodio 2 — Revisar disponibilidad y límites de intervalos

**Objetivo e instrucción:** revisar si la consulta de disponibilidad y la creación de reservas aplican la misma regla para intervalos `[inicio, fin)`, y comprobar superposición, horarios consecutivos y unidades distintas. No cambiar `inventory.json` ni agregar funciones para editar el inventario; si hubiera una carencia, añadir una prueba enfocada y una corrección mínima, y luego ejecutar la suite completa.

**Acción y resultado observado:** se inspeccionaron `ReservationService._has_conflict`, `available_units` y `create`. Ambas operaciones usan la misma detección de conflicto: solo cuenta reservas activas de la misma unidad y usa `inicio_nuevo < fin_existente` junto con `inicio_existente < fin_nuevo`. No se detectó una carencia, así que no se modificó código ni se necesitó agregar una prueba. `inventory.json` no se modificó.

**Pruebas ejecutadas:** cuatro pruebas enfocadas pasaron: `test_availability_uses_the_same_interval_rules`, `test_rejects_overlapping_active_reservation`, `test_allows_consecutive_reservations` y `test_allows_same_time_on_different_units`. Después, `python -m unittest discover -s tests -v` ejecutó la suite completa: 9 pruebas pasaron. Entorno observado: Python 3.13.14. `git diff --check` no reportó errores.

**Decisión humana:** no se informó una decisión separada sobre aceptar, corregir o rechazar; la revisión no encontró cambios que requirieran esa decisión.

**Evidencia:** las pruebas están definidas en `tests/test_reservation_app.py`. Los comandos se ejecutaron en la terminal durante esta sesión; no se guardó una transcripción de terminal aparte.

#### Episodio 3 — Comprobar cancelación y persistencia entre ejecuciones

Prueba el flujo de consola con un archivo JSON temporal propio, para no leer ni modificar el archivo de datos habitual. El nombre de solicitante y las fechas del siguiente ejemplo son datos sintéticos de prueba, no reservas reales. Ejecuta cada comando en la misma terminal de PowerShell:

```powershell
$dataFile = Join-Path $env:TEMP ("reservas-prueba-" + [guid]::NewGuid().ToString() + ".json")
python --version
python reservation_app.py --data-file $dataFile reserve --unit MIC-01 --requester "Prueba ficticia" --start 2030-04-15T10:00 --end 2030-04-15T11:00
python reservation_app.py --data-file $dataFile list
```

Copia el ID que realmente imprimió `reserve` y úsalo en los comandos siguientes. La segunda reserva debe rechazarse por superposición; la consecutiva debe permitirse; después cancela la primera y comprueba con `list` que sigue en el historial como cancelada:

```powershell
python reservation_app.py --data-file $dataFile reserve --unit MIC-01 --requester "Otra prueba ficticia" --start 2030-04-15T10:30 --end 2030-04-15T11:30
python reservation_app.py --data-file $dataFile reserve --unit MIC-01 --requester "Prueba consecutiva" --start 2030-04-15T11:00 --end 2030-04-15T12:00
python reservation_app.py --data-file $dataFile cancel --id ID_REAL_COPIADO_DE_LA_SALIDA
python reservation_app.py --data-file $dataFile list
```

El proceso de cada comando termina antes de iniciar el siguiente, así que `list` comprueba que los datos se recuperan del archivo. Conserva el archivo temporal mientras necesites verificar el resultado; no uses ni borres el archivo habitual `data/reservations.json` para esta prueba.

#### Qué registrar en el episodio 3

Al completar el episodio 3, registra solo lo que haya ocurrido:

- **Objetivo y requisito:** qué comportamiento se revisó.
- **Instrucción al agente:** la tarea concreta que se le pidió.
- **Acción y resultado observado:** archivos modificados (si los hubo), comandos ejecutados y salida real; distingue las propuestas del agente de las acciones que efectivamente se ejecutaron.
- **Decisión humana:** aceptado, corregido o rechazado, con un motivo breve.
- **Evidencia:** enlaces a los archivos y, si se guardó, a una captura o transcripción de comandos sin datos personales innecesarios.

Los resultados de pruebas y la versión de Python deben copiarse del entorno donde se ejecuten. Los ejemplos anteriores no son evidencia de reservas reales. Para usar reservas reales, utiliza únicamente datos autorizados para la entrega, minimiza datos personales y no alteres el inventario fijo.

### Resultados de verificación ejecutados por la persona

Completa esta tabla con resultados observados en el entorno de entrega. No confundas una afirmación del agente con una ejecución comprobada.

| Comando o procedimiento | Versión de Python | Resultado observado |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | 3.13.14 | 9 pruebas pasaron |
| `reserve` → `list` en otro proceso → `cancel` → `list` en otro proceso, usando `--data-file` temporal | 3.13.14 | La reserva activa y luego su estado cancelado persistieron tras reiniciar; `PERSISTENCE SMOKE TEST: OK` |
