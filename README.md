# Detección de objetos en tiempo real

Aplicación web desarrollada con **Django, OpenCV y PostgreSQL** para detectar
objetos mediante una cámara, mostrar sus etiquetas en español y guardar los
resultados en un historial.

El detector utiliza **YOLO-World preentrenado** con una lista de objetos
configurada mediante texto. El proyecto no entrena un modelo desde cero.

Proyecto académico de **Construcción de Software — Universidad Estatal de
Milagro (UNEMI)**.

## Funcionalidades

- Iniciar y detener la captura de la cámara desde la página web.
- Detectar objetos y dibujar sus recuadros, nombres en español y confianza.
- Guardar manualmente los objetos del último fotograma analizado.
- Consultar los últimos 50 registros y el total de detecciones guardadas.
- Actualizar el historial sin recargar toda la página.
- Mostrar la fecha y hora del historial en la zona `America/Guayaquil`.
- Conservar los registros en PostgreSQL después de cerrar la página.

Se almacenan **nombre del objeto, confianza y fecha de guardado**. No se
almacenan fotografías ni grabaciones de video.

## Tecnologías

| Tecnología | Uso en el proyecto |
| --- | --- |
| Python | Lógica del servidor |
| Django | Vistas, rutas, sesiones y acceso a la base de datos |
| OpenCV (`cv2`) | Captura de la cámara, anotación y codificación de imágenes |
| Ultralytics / YOLO-World | Detección de objetos mediante un modelo preentrenado |
| CLIP | Conversión de los nombres de búsqueda en representaciones para el modelo |
| PostgreSQL | Persistencia del historial |
| Psycopg | Conexión entre Django y PostgreSQL |
| python-dotenv | Lectura de la configuración local desde `.env` |
| HTML, CSS y JavaScript | Interfaz, controles y actualización del historial |

El entorno de desarrollo utilizado es **Windows, Python 3.14.7, Django 6.1.3
y PostgreSQL 18**. Las versiones de las dependencias se registran en
`requirements.txt`.

## Objetos configurados

Los textos de búsqueda se establecen en inglés y los resultados se muestran
en español. La configuración actual contiene estas 12 categorías:

| Texto de búsqueda | Etiqueta en la interfaz |
| --- | --- |
| `person` | Persona |
| `bottle` | Botella |
| `cell phone` | Celular |
| `apple` | Manzana |
| `computer mouse` | Mouse |
| `eyeglasses` | Lentes |
| `medical face mask` | Mascarilla |
| `shoe` | Zapato |
| `keyboard` | Teclado |
| `laptop` | Laptop |
| `book` | Libro |
| `chair` | Silla |

Esta lista indica qué objetos se buscan; no garantiza que todos se detecten
correctamente en cualquier condición. La iluminación, distancia, tamaño,
orientación y presencia de objetos que los tapan afectan el resultado.

## Requisitos previos

- Windows con Python y pip instalados.
- PostgreSQL en ejecución y credenciales para crear y utilizar una base de datos.
- Una cámara disponible en el equipo que ejecutará Django.
- Acceso a internet para instalar las dependencias y descargar los modelos
  durante la primera ejecución.

Los comandos siguientes se ejecutan en **PowerShell**, desde la carpeta del
proyecto donde se encuentra `manage.py`.

## Instalación

### 1. Obtener el código

Clona este repositorio o descarga su ZIP desde **Code → Download ZIP** en GitHub.
Si descargas el ZIP, extráelo y abre la carpeta del proyecto en tu editor.

### 2. Crear el entorno virtual

```powershell
py -m venv .venv
```

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

Se utiliza directamente el ejecutable de `.venv`, por lo que no es necesario
activar el entorno virtual.

### 3. Instalar las dependencias

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

El archivo de dependencias debe incluir CLIP. Si la importación de `clip`
falla porque no quedó instalado, puede instalarse desde su repositorio oficial:

```powershell
.\.venv\Scripts\python.exe -m pip install "https://github.com/openai/CLIP/archive/refs/heads/main.zip"
```

Comprueba las importaciones:

```powershell
.\.venv\Scripts\python.exe -c "import django, cv2, ultralytics, psycopg, dotenv, clip; print('Dependencias disponibles')"
```

### 4. Crear la base de datos

En pgAdmin, conéctate al servidor PostgreSQL y selecciona:

**Databases → clic derecho → Create → Database…**

Utiliza el nombre `deteccion_objetos` y, para esta demostración local, el
propietario `postgres`.

También puedes ejecutar el siguiente SQL en una conexión existente al servidor,
con un usuario que tenga permiso para crear bases:

```sql
CREATE DATABASE deteccion_objetos;
```

Elige uno de los dos métodos. La base solo debe crearse una vez.

### 5. Configurar las credenciales

Crea un archivo llamado `.env` junto a `manage.py`:

```dotenv
DB_NAME=deteccion_objetos
DB_USER=postgres
DB_PASSWORD='CAMBIA_ESTO_POR_TU_CONTRASEÑA'
DB_HOST=localhost
DB_PORT=5432
```

Reemplaza la contraseña de ejemplo por la de tu instalación. Ajusta usuario,
host y puerto si utilizas una configuración diferente. `.env` debe permanecer
excluido del repositorio mediante `.gitignore`.

El proyecto carga estas variables en `config/settings.py` y utiliza el motor
`django.db.backends.postgresql`.

### 6. Aplicar las migraciones

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Las migraciones incluidas crean las tablas de Django y la tabla del modelo
`Deteccion`. Al instalar el proyecto desde el repositorio se aplican las
migraciones existentes; `makemigrations` se utiliza al modificar los modelos.

### 7. Revisar y ejecutar

```powershell
.\.venv\Scripts\python.exe manage.py check
```

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abre **http://127.0.0.1:8000/** en el navegador y pulsa **Iniciar detección**.

La primera vez que se inicia el detector se descargan el archivo
`yolov8s-worldv2.pt` y los recursos del codificador de texto que falten. La carga
inicial puede tardar. Estos archivos no se incluyen en GitHub.

## Cómo utilizar la aplicación

1. Pulsa **Iniciar detección** y espera a recibir imágenes de la cámara.
2. Coloca un objeto frente a ella y observa el recuadro, la etiqueta y la confianza.
3. Cuando haya resultados recientes, se habilita **Guardar detección**.
4. Pulsa el botón para registrar los objetos del último fotograma analizado.
5. Consulta los registros en **Historial de detecciones**. El historial se
   actualiza después del guardado y también dispone de un botón de actualización.
6. Pulsa **Detener** para finalizar la transmisión y liberar la cámara.

Cada objeto detectado genera un registro. Por ejemplo, si aparecen una persona
y una botella, un clic guarda dos registros. No se guarda automáticamente cada
fotograma. Guardar en fotogramas distintos puede crear nuevos registros del
mismo objeto; el sistema no identifica objetos únicos a lo largo del tiempo.

La confianza se almacena entre `0` y `1` y se muestra como porcentaje. Es una
puntuación del modelo y no una garantía de que la identificación sea correcta.

## Organización del código

| Archivo o directorio | Responsabilidad |
| --- | --- |
| `manage.py` | Comandos de administración del proyecto |
| `config/settings.py` | Configuración general y conexión con PostgreSQL |
| `config/urls.py` | Rutas principales del proyecto |
| `detector/models.py` | Modelo `Deteccion` |
| `detector/views.py` | Captura, inferencia, transmisión, guardado e historial |
| `detector/urls.py` | Rutas de la aplicación |
| `detector/templates/detector/inicio.html` | Página, estilos y controles |
| `detector/migrations/` | Cambios de estructura de la base de datos |
| `requirements.txt` | Dependencias y versiones del entorno |
| `.gitignore` | Archivos excluidos del repositorio |

### Flujo de procesamiento

1. OpenCV captura un fotograma de la cámara del equipo servidor.
2. YOLO-World analiza la imagen utilizando los textos de búsqueda configurados.
3. El servidor dibuja las etiquetas en español y transmite el fotograma como JPEG.
4. El último resultado se mantiene temporalmente en memoria, asociado a la
   sesión del navegador.
5. Al guardar, una solicitud POST protegida con CSRF escribe los resultados en
   PostgreSQL mediante el ORM de Django y una transacción.
6. El historial consulta los registros persistentes y actualiza la tabla de la interfaz.

### Rutas

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/` | Página principal |
| GET | `/video/` | Transmisión de imágenes con detecciones |
| GET | `/estado/` | Disponibilidad y cantidad de resultados recientes |
| POST | `/detener/` | Solicitud para detener la transmisión |
| POST | `/guardar/` | Guardado manual del último resultado |
| GET | `/historial/` | Últimos 50 registros y total guardado |

### Datos almacenados

La tabla generada por Django para este modelo es `detector_deteccion`.

| Campo | Contenido |
| --- | --- |
| `id` | Identificador automático |
| `objeto` | Nombre del objeto detectado |
| `confianza` | Puntuación del modelo entre 0 y 1 |
| `fecha` | Fecha y hora de creación del registro |

`porcentaje` es una propiedad calculada del modelo, no una columna adicional.

## Rendimiento y alcance

La configuración de inferencia utiliza `imgsz=320`, `conf=0.25` y `device="cpu"`.
Se eligió el tamaño 320 para mejorar la fluidez observada durante las pruebas.
Una resolución mayor puede ayudar con detalles pequeños, pero aumenta la carga.

Esta versión está preparada para una **demostración local con `runserver`, un
proceso y una cámara activa**. La cámara utilizada pertenece al equipo donde
se ejecuta Django, aunque la interfaz se abra desde otro dispositivo. Usa una
sola pestaña para la prueba. El historial es común al proyecto y no está separado
por cuentas de usuario.

El último fotograma analizado es temporal; los registros guardados permanecen
en PostgreSQL. El servidor de desarrollo no constituye una configuración de
despliegue en producción.

## Comprobación funcional

| Prueba | Resultado esperado |
| --- | --- |
| Iniciar detección | Aparece el video con etiquetas en español |
| Mostrar un objeto reconocible | Aparece un recuadro y una confianza |
| Guardar con objetos visibles | Se muestra una confirmación y se agregan registros |
| Detener | Se interrumpe el video y se solicita liberar la cámara |
| Recargar la página | Los registros guardados siguen en el historial |
| Reiniciar Django | Los registros de PostgreSQL permanecen |

Para consultar el total directamente desde Django:

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "from detector.models import Deteccion; print('Registros guardados:', Deteccion.objects.count())"
```

## Problemas frecuentes

| Problema | Revisión sugerida |
| --- | --- |
| La cámara está ocupada | Cierra otras aplicaciones o transmisiones que la utilicen |
| El video tarda al iniciar | Espera la carga o descarga inicial del modelo y revisa la terminal |
| La imagen se mueve lentamente | Conserva `imgsz=320` y revisa la carga del procesador |
| Un objeto no se detecta | Revisa los textos configurados, iluminación, distancia y visibilidad |
| No se habilita Guardar | Espera a que haya objetos detectados y resultados recientes |
| Error de conexión a PostgreSQL | Verifica el servicio, la base y las variables de `.env` |
| No existe la tabla de detecciones | Ejecuta `manage.py migrate` con el Python del entorno |
| Error 403 al guardar | Recarga la página en el mismo host y conserva las cookies y la protección CSRF |

## Preparación del repositorio

Incluye el código fuente, `README.md`, `requirements.txt` y las migraciones.
Excluye el entorno virtual, `.env`, los modelos descargados (`*.pt`), cachés y
resultados temporales mediante `.gitignore`.

Para actualizar el archivo de dependencias desde el entorno del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip freeze | Out-File -Encoding utf8 requirements.txt
```

## Documentación de las herramientas

- [Django](https://docs.djangoproject.com/en/6.1/)
- [OpenCV](https://docs.opencv.org/)
- [YOLO-World en Ultralytics](https://docs.ultralytics.com/models/yolo-world/)
- [Repositorio original de YOLO-World](https://github.com/AILab-CVC/YOLO-World)
- [CLIP](https://github.com/openai/CLIP)
- [PostgreSQL](https://www.postgresql.org/docs/)

Se utilizan herramientas y modelos de terceros. Sus licencias y autorías
corresponden a sus respectivos proyectos; configurar los textos de búsqueda
no implica haber entrenado el modelo original.
