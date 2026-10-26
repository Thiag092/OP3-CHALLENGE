# Sistema local de reservas de equipos

Este proyecto consiste en una aplicación de consola hecha en Python para
gestionar reservas de equipos de un laboratorio. Permite consultar qué
unidades están disponibles en un determinado horario, crear reservas y
cancelarlas sin eliminar su información.

El proyecto utiliza Python 3.10 o superior y solamente la biblioteca
estándar. Las reservas se guardan localmente en un archivo JSON, por lo
que no es necesario instalar una base de datos ni utilizar servicios
externos.

## Funcionamiento

El inventario de equipos se encuentra definido en `inventory.json`. Cada
ID representa una unidad física diferente y el inventario es fijo, es
decir, desde la aplicación no se pueden agregar, modificar ni eliminar
unidades.

El sistema permite:

-   Consultar qué unidades están disponibles entre dos fechas y horas.
-   Crear una reserva indicando unidad, solicitante, inicio y fin.
-   Evitar que una misma unidad tenga dos reservas activas superpuestas.
-   Reservar unidades diferentes en el mismo horario.
-   Realizar reservas consecutivas.
-   Cancelar una reserva sin eliminarla del historial.
-   Mantener las reservas guardadas aunque se cierre y vuelva a ejecutar
    el programa.

Para manejar los horarios se utilizan intervalos semiabiertos
`[inicio, fin)`. Esto significa que, por ejemplo, si una reserva termina
a las 11:00, otra puede comenzar exactamente a las 11:00 sin que exista
superposición.

Las fechas deben ingresarse con el formato `AAAA-MM-DDTHH:MM` y se
utiliza la hora local, sin zona horaria. También se verifica que la
unidad exista, que el nombre del solicitante no esté vacío y que la
fecha de inicio sea anterior a la fecha de finalización.

No se bloquearon fechas pasadas ni se establecieron límites máximos de
duración o anticipación, ya que la consigna no especificaba esas
restricciones.

## Estructura del proyecto

La lógica principal y los comandos de consola se encuentran en
`reservation_app.py`.

El archivo `inventory.json` contiene las cinco unidades disponibles
inicialmente y se carga al ejecutar los comandos.

Las pruebas automatizadas se encuentran en `tests/` y fueron realizadas
utilizando `unittest`.

Las reservas se almacenan por defecto en:

`data/reservations.json`

Este archivo se crea automáticamente al guardar la primera reserva. Para
evitar problemas durante la escritura, primero se genera un archivo
temporal y luego se reemplaza el archivo anterior.

No se recomienda borrar `reservations.json`, ya que contiene el
historial de reservas. Para realizar pruebas sin modificar los datos
normales se puede utilizar otro archivo mediante `--data-file`.

## Cómo ejecutar el proyecto

Desde la carpeta raíz del proyecto se puede comprobar primero la versión
de Python:

``` powershell
python --version
```

Para ejecutar todas las pruebas:

``` powershell
python -m unittest discover -s tests -v
```

Para listar las reservas:

``` powershell
python reservation_app.py list
```

Consultar disponibilidad:

``` powershell
python reservation_app.py availability --start 2030-04-15T10:00 --end 2030-04-15T11:00
```

Crear una reserva:

``` powershell
python reservation_app.py reserve --unit MIC-01 --requester "Ana" --start 2030-04-15T10:00 --end 2030-04-15T11:00
```

Volver a listar las reservas:

``` powershell
python reservation_app.py list
```

Cancelar una reserva:

``` powershell
python reservation_app.py cancel --id ID_QUE_MUESTRA_LA_RESERVA
```

Por ejemplo, si `MIC-01` está reservado de 10:00 a 11:00, una nueva
reserva para esa unidad entre 10:30 y 11:30 será rechazada porque existe
una superposición.

En cambio, una reserva de 11:00 a 12:00 será aceptada porque los
intervalos son consecutivos. También sería posible reservar `MIC-02` de
10:00 a 11:00 porque se trata de otra unidad física.

Una de las pruebas realizadas desde la consola produjo el siguiente
resultado:

``` text
Reserva cancelada: res_868123f2572a | MIC-01 (Microscopio digital) | Prueba ficticia | 2030-04-15T10:00 a 2030-04-15T11:00 | cancelled
res_868123f2572a | MIC-01 (Microscopio digital) | Prueba ficticia | 2030-04-15T10:00 a 2030-04-15T11:00 | cancelled
res_3743c69cbc12 | MIC-01 (Microscopio digital) | Prueba consecutiva | 2030-04-15T11:00 a 2030-04-15T12:00 | active
```

La salida completa de esta prueba está guardada en
`evidence/episodio-3-cli-smoke.txt`.

## Uso del agente de programación

Para desarrollar y revisar el proyecto se utilizó un agente de
programación desde Visual Studio Code con Copilot SDK, trabajando
directamente sobre los archivos del repositorio.

El identificador y la versión exacta del modelo utilizado no fueron
visibles desde el entorno.

Las instrucciones específicas para el agente se encuentran en
`.github/copilot-instructions.md`.

En este archivo se definieron reglas relacionadas con la superposición
de reservas, los intervalos consecutivos, la disponibilidad, la
cancelación, la persistencia y la necesidad de informar únicamente
pruebas que realmente hayan sido ejecutadas.

También se utilizó como referencia la consigna original
`challenge-agents.pdf`, además del código, las pruebas y el inventario
del proyecto.

No se utilizaron credenciales, datos personales reales ni servicios
externos. Para las pruebas manuales se trabajó con solicitantes
ficticios y un archivo JSON temporal, evitando modificar tanto
`inventory.json` como el archivo normal de reservas.

## Prompt original

> Necesito una aplicación local de consola para reservar equipos de
> laboratorio. Usa Python 3.10 o posterior y, salvo que haya una razón
> justificada, solo la biblioteca estándar. Persiste las reservas en un
> archivo JSON local.
>
> El inventario inicial está definido en inventory.json y no se debe
> poder agregar, editar ni eliminar unidades desde la aplicación. Cada
> ID representa una unidad física distinta.
>
> La aplicación debe permitir consultar qué unidades están disponibles
> para un intervalo, crear una reserva y cancelarla. Cada reserva guarda
> un ID, unidad, equipo, solicitante ficticio, fecha y hora de inicio y
> fin, y estado.
>
> Trata los intervalos como \[inicio, fin): para la misma unidad,
> rechaza reservas activas superpuestas, permite reservas consecutivas y
> permite reservar unidades distintas al mismo tiempo. Las canceladas
> deben conservar el mismo ID y sus datos originales, pero no bloquear
> disponibilidad.
>
> Valida que la unidad exista, que el solicitante no esté vacío ni
> compuesto solo por espacios, que las fechas tengan formato
> AAAA-MM-DDTHH:MM y que el inicio sea anterior al fin. Usa hora local
> sin zona horaria. Documenta cómo se tratan fechas pasadas y límites de
> duración o anticipación.
>
> Primero inspecciona el repositorio y sus instrucciones. Haz cambios
> pequeños y explica qué archivos modificas y por qué. No agregues
> servicios externos ni dependencias innecesarias. Incluye pruebas
> automatizadas para creación válida, entradas inválidas, superposición,
> intervalos consecutivos, unidades distintas, cancelación, liberación
> del horario y persistencia tras reiniciar. Ejecuta
> `python -m unittest discover -s tests -v` y comunica el resultado
> observado, sin afirmar pruebas no ejecutadas.
>
> Actualiza el README con la especificación, decisiones técnicas,
> instalación y comandos, persistencia, límites, pruebas y evidencia
> real del uso del agente. No inventes resultados ni datos personales;
> usa solicitantes ficticios.

## Desarrollo y pruebas realizadas

### Primera versión

En una primera etapa se generó la base funcional de la aplicación: la
interfaz de consola, el inventario inicial, la persistencia en JSON y
las pruebas.

Esta versión quedó registrada en el commit `f0dcc85` y los archivos
principales fueron:

-   `reservation_app.py`
-   `inventory.json`
-   `tests/test_reservation_app.py`

### Revisión de disponibilidad y superposiciones

Después se revisó especialmente la forma en que se detectaban las
reservas superpuestas.

Se comprobaron `ReservationService._has_conflict`, `available_units` y
`create`.

La condición utilizada para detectar una superposición es:

`inicio_nuevo < fin_existente`

junto con:

`inicio_existente < fin_nuevo`

Solamente se tienen en cuenta reservas activas correspondientes a la
misma unidad.

Al revisar esta parte no se encontraron errores, por lo que no fue
necesario modificar la lógica ni agregar otra prueba. Tampoco se
modificó `inventory.json`.

Se ejecutaron específicamente estas cuatro pruebas:

-   `test_availability_uses_the_same_interval_rules`
-   `test_rejects_overlapping_active_reservation`
-   `test_allows_consecutive_reservations`
-   `test_allows_same_time_on_different_units`

Las cuatro finalizaron correctamente.

Luego se ejecutó la suite completa:

``` powershell
python -m unittest discover -s tests -v
```

El resultado fue de **9 pruebas aprobadas** utilizando Python
**3.13.14**.

También se ejecutó:

``` powershell
git diff --check
```

sin obtener errores.

## Prueba de cancelación y persistencia

También se realizó una prueba manual utilizando la aplicación desde la
consola y un `--data-file` temporal.

Cada comando se ejecutó en un proceso nuevo para comprobar que los datos
realmente se conservaran entre distintas ejecuciones del programa.

Durante esta prueba:

-   Se creó una reserva.
-   Se intentó crear otra superpuesta y fue rechazada con código de
    salida 1.
-   Se creó correctamente una reserva consecutiva.
-   Se canceló la primera reserva.
-   La reserva cancelada conservó su mismo ID y sus datos.
-   La reserva consecutiva continuó con estado `active`.
-   Al volver a consultar disponibilidad, `MIC-01` apareció nuevamente
    disponible en el horario que había sido liberado.

Esto permitió comprobar tanto la persistencia entre ejecuciones como el
comportamiento de las cancelaciones.

La salida completa de esta prueba, junto con la versión de Python y los
códigos de salida, se encuentra en `evidence/episodio-3-cli-smoke.txt`.

## Resultado de las pruebas

Las verificaciones se realizaron con Python **3.13.14**.

  -----------------------------------------------------------------------
  Prueba                              Resultado
  ----------------------------------- -----------------------------------
  4 pruebas específicas de            4 aprobadas
  disponibilidad y superposición      

  Prueba manual desde CLI con archivo Superposición rechazada, reserva
  temporal                            consecutiva aceptada, cancelación
                                      conservada y horario liberado

  Suite completa con `unittest`       9 pruebas aprobadas
  -----------------------------------------------------------------------

La ejecución completa de las pruebas fue:

``` text
test_active_and_cancelled_records_survive_restart (test_reservation_app.ReservationServiceTests.test_active_and_cancelled_records_survive_restart) ... ok
test_allows_consecutive_reservations (test_reservation_app.ReservationServiceTests.test_allows_consecutive_reservations) ... ok
test_allows_same_time_on_different_units (test_reservation_app.ReservationServiceTests.test_allows_same_time_on_different_units) ... ok
test_availability_uses_the_same_interval_rules (test_reservation_app.ReservationServiceTests.test_availability_uses_the_same_interval_rules) ... ok
test_cancel_keeps_record_and_releases_interval (test_reservation_app.ReservationServiceTests.test_cancel_keeps_record_and_releases_interval) ... ok
test_creates_valid_reservation (test_reservation_app.ReservationServiceTests.test_creates_valid_reservation) ... ok
test_rejects_invalid_interval (test_reservation_app.ReservationServiceTests.test_rejects_invalid_interval) ... ok
test_rejects_overlapping_active_reservation (test_reservation_app.ReservationServiceTests.test_rejects_overlapping_active_reservation) ... ok
test_rejects_unknown_unit_and_blank_requester (test_reservation_app.ReservationServiceTests.test_rejects_unknown_unit_and_blank_requester) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.066s
```

Con estas pruebas se comprobó el funcionamiento de la creación de
reservas, las validaciones, la detección de superposiciones, los
intervalos consecutivos, las reservas simultáneas sobre unidades
diferentes, la cancelación y la persistencia de los datos entre
ejecuciones.
