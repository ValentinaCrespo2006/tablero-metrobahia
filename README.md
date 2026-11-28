# Tablero MetroBahía

Proyecto de Inteligencia de Negocios — Grupo 3 | Universidad Autónoma del Caribe.

## Descripción del proyecto

MetroBahía es un sistema de inteligencia de negocios para analizar la demanda, los ingresos por pasajes y el cumplimiento de despachos del servicio de transporte. El proyecto integra PostgreSQL, Python y Dash para procesar archivos del cliente, preservar la trazabilidad y generar indicadores de apoyo a la toma de decisiones.

## Propósito

Centralizar la información del cliente, controlar su calidad, facilitar el trabajo colaborativo y proporcionar indicadores confiables para la gestión operativa y financiera.

## Integrantes del equipo

| Rol | Nombre | Usuario de GitHub |
| --- | --- | --- |
| Líder del proyecto y analista de negocio | Dionisio Ortega | [dionisioortega00](https://github.com/dionisioortega00) |
| Ingeniero de datos | Erick Mendoza | [Erick0078](https://github.com/Erick0078) |
| Diseñador de la lógica | Gustavo Tapias | [gustavo031876](https://github.com/gustavo031876) |
| Desarrollador de pantallas | David Ospino | [DavidOspino2005](https://github.com/DavidOspino2005) |
| Responsable de calidad y despliegue | Valentina Crespo | [ValentinaCrespo2006](https://github.com/ValentinaCrespo2006) |

### Responsabilidades por integrante

- **Dionisio Ortega – Líder del proyecto y analista de negocio:** habla por el cliente y representa sus decisiones, indicadores y metas. Lleva este documento y lo sube en cada momento.
- **Erick Mendoza – Ingeniero de datos:** diseña la base de datos y programa la carga de los archivos: lectura, revisión fila por fila, rechazo y registro.
- **Gustavo Tapias – Diseñador de la lógica:** programa el cálculo de los indicadores y semáforos, los filtros, el inicio de sesión y los perfiles.
- **David Ospino – Desarrollador de pantallas:** diseña y programa las pantallas, las gráficas, el detalle con clic y la versión para celular. En el Momento 2 publicó `app.py` y `docs/captura_carga_metrobahia.png`.
- **Valentina Crespo – Responsable de calidad y despliegue:** programa las pruebas automáticas, cuida el repositorio y las publicaciones, y lleva el registro de decisiones. En el Momento 2 publicó `tests/test_carga.py`, `docs/pruebas_locales.txt`, `docs/captura_pruebas_automaticas.png`, `.env.ejemplo`, `.gitignore`, `requirements.txt` y `README.md`.


## Estado del proyecto

| Momento | Alcance | Estado |
|---|---|---|
| 1 | Análisis del cliente, indicadores, diseño de base de datos y boceto | Documentado |
| 2 | Base de datos, carga controlada, consultas SQL y pruebas | Implementado, verificado localmente y publicado en GitHub |
| 3 | Tablero interactivo, filtros, semáforos y perfiles | Etapa siguiente |
| 4 | Pruebas finales y publicación web | Etapa siguiente |

## Tecnologías y entorno verificado

- PostgreSQL 18, puerto local 5433, base de datos `metrobahia`.
- Python 3.13.7, Dash 4.5.2 y pytest 9.2.0.
- pgAdmin 4, Visual Studio Code, Openpyxl, Psycopg2 y Python-dotenv.
- GitHub para control de versiones y colaboración.

## Estructura del repositorio al cierre del Momento 2

```text
tablero-metrobahia/
├── README.md
├── Proyecto_BI_Grupo3_Momento1.pdf
├── Proyecto_BI_Grupo3_Momento2.pdf  (documento acumulativo para EXIA y GitHub)
├── Formulas_indicadores.pdf
├── app.py
├── carga.py
├── persistencia.py
├── esquema.sql
├── indicadores.sql
├── requirements.txt
├── .env.ejemplo
├── .gitignore
├── datos_cliente/
│   ├── rutas.xlsx
│   ├── estaciones.csv
│   ├── validaciones.xlsx
│   └── despachos.xlsx
├── tests/
│   └── test_carga.py
└── docs/
    ├── diagrama_base_de_datos.png
    ├── boceto_tablero.png
    ├── captura_pruebas_automaticas.png
    ├── pruebas_locales.txt
    └── captura_carga_metrobahia.png
```

`esquema.sql` crea las ocho tablas; `carga.py` valida y normaliza los registros; `persistencia.py` almacena los datos y rechazos; `indicadores.sql` contiene las consultas de negocio; `app.py` proporciona la interfaz de carga y reportes históricos. Las tablas `cargas` y `rechazos` tienen las vistas de consulta `archivo_carga` y `fila_rechazada`, respectivamente.

## Archivos originales del cliente

Los cuatro archivos originales se conservan sin modificaciones en la carpeta [`datos_cliente/`](datos_cliente/). Los enlaces relativos permiten abrir o descargar cada archivo directamente desde el repositorio.

| Archivo | Ruta en el repositorio | Descripción |
|---|---|---|
| [rutas.xlsx](datos_cliente/rutas.xlsx) | `datos_cliente/rutas.xlsx` | Catálogo de rutas de transporte. |
| [estaciones.csv](datos_cliente/estaciones.csv) | `datos_cliente/estaciones.csv` | Catálogo de estaciones y sus características. |
| [validaciones.xlsx](datos_cliente/validaciones.xlsx) | `datos_cliente/validaciones.xlsx` | Registros de validaciones, tipos de tarjeta y valores de pasajes. |
| [despachos.xlsx](datos_cliente/despachos.xlsx) | `datos_cliente/despachos.xlsx` | Registros de despachos programados y realizados por ruta y franja. |

## Instalación y ejecución local (Windows)

1. Descargar o clonar el repositorio y abrir su carpeta en Visual Studio Code.
2. Crear el entorno virtual e instalar dependencias:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

3. Crear una base vacía `metrobahia` en pgAdmin. Ejecutar `esquema.sql` desde Query Tool de esa base.
4. Copiar `.env.ejemplo` a `.env` y configurar la conexión con las credenciales propias. Ejemplo ficticio (ajustar el puerto al servidor local):

```dotenv
DATABASE_URL=postgresql://postgres:CAMBIAR_CONTRASENA@localhost:5433/metrobahia
```

5. Verificar la conexión:

```powershell
.\.venv\Scripts\python.exe -c "from persistencia import conectar; c=conectar(); print('Conexion exitosa a PostgreSQL'); c.close()"
```

6. Iniciar Dash:

```powershell
.\.venv\Scripts\python.exe app.py
```

Abrir http://127.0.0.1:8050/. En una base vacía, cargar una sola vez y en este orden: rutas, estaciones, validaciones y despachos. Si los archivos ya están cargados, seleccionar el reporte histórico sin volver a cargarlos. Como alternativa a la carga inicial mediante Dash, `python persistencia.py` realiza la carga por consola; no utilizar ambas modalidades sobre los mismos archivos.

7. Ejecutar las consultas de `indicadores.sql` en pgAdmin y las pruebas desde la raíz:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

## Momento 2 — Resultados de la ejecución local

Periodo de los datos: 01/11/2025 a 31/10/2026. La carga se realizó el 27 y 28 de noviembre de 2026.

| Archivo | Leídas | Cargadas | Rechazadas |
|---|---:|---:|---:|
| [rutas.xlsx](datos_cliente/rutas.xlsx) | 3 | 3 | 0 |
| [estaciones.csv](datos_cliente/estaciones.csv) | 14 | 14 | 0 |
| [validaciones.xlsx](datos_cliente/validaciones.xlsx) | 69.930 | 68.871 | 1.059 |
| [despachos.xlsx](datos_cliente/despachos.xlsx) | 4.404 | 4.345 | 59 |
| **Total** | **74.351** | **73.233** | **1.118** |

La conciliación de las cuatro cargas conservadas fue correcta: leídas = cargadas + rechazadas. Los conteos de las tablas se verificaron en PostgreSQL. La aceptación fue del 98,50 %.

### Motivos de rechazo

| Archivo | Motivo | Filas |
|---|---|---:|
| validaciones.xlsx | Fila duplicada / llave repetida | 343 |
| validaciones.xlsx | Pasaje no numérico | 253 |
| validaciones.xlsx | Fecha vacía | 176 |
| validaciones.xlsx | Pasaje negativo | 174 |
| validaciones.xlsx | Estación inexistente | 113 |
| despachos.xlsx | Fila duplicada / llave repetida | 21 |
| despachos.xlsx | Realizados no numérico | 15 |
| despachos.xlsx | Fecha vacía | 10 |
| despachos.xlsx | Realizados negativo | 10 |
| despachos.xlsx | Fila SUBTOTAL | 3 |
| **Total** | | **1.118** |

Se normalizan formatos inequívocos mediante el programa; se rechazan los datos que exigirían inventar valores. Durante el desarrollo hubo dos recargas accidentales sin inserciones nuevas (estaciones y validaciones). Se retiraron manualmente del historial local junto con sus rechazos; este ajuste queda documentado para revisión del docente por la regla de trazabilidad. No se alteraron los archivos originales.

### Indicadores calculados en PostgreSQL

| Indicador | Resultado local |
|---|---|
| Cumplimiento de despachos | 94,73 % (39.075 de 41.247) |
| Validaciones por día hábil | 222,22 (57.778 / 260 días de lunes a viernes con datos) |
| Crecimiento mensual de ingresos | +1,25 % en octubre de 2026 |
| Déficit diario de despachos | 5,95 (2.172 / 365 días) |
| Participación de tarifa reducida | 25,03 % (17.241 / 68.871 validaciones) |
| Presión por franja | Pico mañana 2,66; valle 1,70; pico tarde 2,48; noche 1,01 |

La presión por franja corresponde a la consulta agregada de R1 y R2 ejecutada en pgAdmin, con horas conocidas; no representa ocupación real de los vehículos. El archivo SQL original agrupa este indicador por ruta y franja; la cifra presentada es una agregación distinta. En una nueva prevalidación de los cuatro archivos originales con la copia local del código se reprodujeron los conteos y los totales de cumplimiento (39.075 / 41.247) y tarifa reducida (17.241 / 68.871), coincidentes con SQL. Esta comprobación no es una segunda implementación independiente de las reglas.

### Interfaz de carga

La aplicación Dash permite visualizar métricas acumuladas y tasa de aceptación general e individual, seleccionar archivos, consultar cargas históricas, observar motivos de rechazo y revisar el detalle de filas rechazadas. La información se recupera de PostgreSQL sin volver a cargar los archivos.

![Captura real del sistema MetroBahía](docs/captura_carga_metrobahia.png)

### Pruebas automáticas

Ejecución local en Windows el 28/11/2026: **4 de 4 pruebas aprobadas en 7,49 segundos**. Las pruebas comprueban fechas vacías, números negativos, conversión de coma decimal y balance de filas en la prevalidación. No equivalen a pruebas automatizadas de integración con PostgreSQL o Dash.

Evidencia: [registro de pruebas](docs/pruebas_locales.txt).

![Evidencia de pruebas automáticas en Visual Studio Code](docs/captura_pruebas_automaticas.png)

## Seguridad y trazabilidad

- El repositorio es público por el carácter académico del proyecto y el origen ficticio de los datos del cliente. No se publican datos personales innecesarios ni credenciales reales.
- No publicar `.env`, contraseñas, entornos virtuales ni archivos de caché. Utilizar `.env.ejemplo` con valores ficticios.
- Conservar los archivos originales sin modificaciones y registrar los resultados y motivos de rechazo.
- No utilizar el servidor de desarrollo de Dash como servidor público. La publicación web corresponde al Momento 4.

## Entregables

- Momento 1: documento, fórmulas, diagrama entidad-relación y boceto del tablero.
- Momento 2: documento en PDF para EXIA, código fuente, archivos originales, pruebas, evidencia real de carga y referencia del último commit.

