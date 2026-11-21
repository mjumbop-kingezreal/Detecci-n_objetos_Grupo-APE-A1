# 📋 Guía de Presentación (5 Minutos) — Detección de Objetos con YOLO-World y Django

> **Materia:** Construcción de Software / Inteligencia Artificial  
> **Institución:** UNEMI  
> **Objetivo:** Exposición puntual, clara y técnica ante el docente/ingeniero.

---

## ⏱️ Distribución de los 5 Minutos

| Minuto | Momento | Objetivo |
| :---: | :--- | :--- |
| **0:00 - 0:45** | **1. Introducción y Propósito** | Qué problema resuelve y alcance del proyecto. |
| **0:45 - 2:00** | **2. Arquitectura Técnica y Stack** | Tecnologías utilizadas y flujo de datos. |
| **2:00 - 3:30** | **3. Demostración en Vivo** | Permisos, detección en directo y guardado manual. |
| **3:30 - 4:30** | **4. Base de Datos y Persistencia** | Historial y optimización de almacenamiento. |
| **4:30 - 5:00** | **5. Conclusiones y Preguntas** | Cierre técnico. |

---

## 🗣️ Guion Paso a Paso para la Explicación

### 1. Introducción y Propósito (0:00 - 0:45)
> *"Buenos días / tardes, Ingeniero(a). Presento el sistema de **Detección de Objetos en Tiempo Real**, desarrollado como parte del trabajo práctico de Construcción de Software.*  
> *El sistema permite capturar video en directo, procesar cada fotograma mediante visión artificial, identificar hasta **12 categorías específicas de objetos** (persona, celular, laptop, botella, etc.) y registrar en base de datos únicamente la metadata relevante sin sobrecargar el servidor con almacenamiento de video."*

---

### 2. Arquitectura y Stack Tecnológico (0:45 - 2:00)
Mencionar los 4 pilares clave:

* **Backend (Django):**
  * Controla el ciclo de vida de la cámara con manejo de hilos y bloqueos (`Lock`) para evitar colisiones de hardware.
  * Transmisión fluida mediante respuestas en flujo (`StreamingHttpResponse`) con protocolo MJPEG.
* **Modelo de Inteligencia Artificial (YOLO-World v2):**
  * Modelo de vocabulario abierto optimizado (`yolov8s-worldv2.pt`).
  * Inferencia local configurada a 320px y confianza mínima de 0.25 para lograr alta tasa de cuadros por segundo (FPS) en CPU.
* **Base de Datos (PostgreSQL):**
  * Modelo relacional `Deteccion` que almacena objeto, nivel de confianza (%) y fecha/hora sincronizada a la zona horaria de Ecuador (`America/Guayaquil`).
* **Frontend y Experiencia de Usuario:**
  * Interfaz profesional, moderna y adaptativa (responsive) con tipografía Inter.
  * Modal interactivo de **confirmación y permiso de cámara** que transparenta la privacidad antes de encender el hardware.

---

### 3. Demostración en Vivo (2:00 - 3:30)
Realizar las siguientes acciones en pantalla:

1. **Abrir la aplicación (`http://127.0.0.1:8000`):**
   * Mostrar el panel principal: estadísticas rápidas (categorías, objetos actuales, registros guardados).
2. **Pulsar «Iniciar detección»:**
   * Mostrar el **modal de solicitud de permiso** explicando que informa al usuario sobre el uso de la cámara y la privacidad (no guarda video).
   * Confirmar permiso: se activa el indicador de estado **"En vivo"** y la transmisión comienza.
3. **Poner objetos frente a la cámara:**
   * Mostrar cómo el modelo encuadra y etiqueta en tiempo real (ej. celular, botella, persona).
   * El contador superior *"Objetos detectados ahora"* se actualiza automáticamente cada segundo vía API (`/estado/`).
4. **Guardar detección:**
   * Presionar **«Guardar detección»**. Explicar que la captura es transaccional y manual para evitar redundancia de datos.

---

### 4. Base de Datos e Historial (3:30 - 4:30)
Mostrar la sección inferior:

* **Tabla de Historial:**
  * Muestra el ID único, nombre del objeto, fecha/hora exacta y **barra gráfica de confianza**.
* **Principio de Eficiencia y Privacidad:**
  * Destacar: *"No guardamos archivos de video pesados en disco ni en base de datos; solo persistimos el resultado inferido (objeto, porcentaje y timestamp), garantizando cumplimiento de privacidad y un consumo mínimo de almacenamiento."*

---

### 5. Cierre y Conclusiones (4:30 - 5:00)
> *"En conclusión, se logró un software robusto, desacoplado, con un consumo controlado de memoria, control de concurrencia en el acceso a la cámara y una interfaz profesional lista para su uso. Quedo atento a cualquier pregunta."*

---

## ❓ Preguntas Frecuentes que te puede hacer el Docente

| Posible Pregunta | Respuesta Clave |
| :--- | :--- |
| **¿Por qué usar YOLO-World en vez de YOLO tradicional?** | YOLO-World permite definir clases personalizadas en tiempo de ejecución mediante embeddings textuales (`set_classes`), haciéndolo más flexible y ligero para las 12 clases elegidas. |
| **¿Cómo se controla que dos usuarios no choquen con la cámara?** | Se implementó un semáforo (`CAMARA_LIBRE = Lock()`) en Django que valida si el recurso ya está tomado, devolviendo un código HTTP 409 si la cámara está en uso. |
| **¿Por qué el video se ve fluido sin WebSockets?** | Se utiliza `StreamingHttpResponse` con límite multiparte (`multipart/x-mixed-replace; boundary=frame`), estándar nativo para streaming MJPEG compatible con cualquier navegador sin librerías externas. |
| **¿Dónde se guardan los datos?** | En PostgreSQL mediante Django ORM con inserciones atómicas (`bulk_create`) para registrar múltiples detecciones en una sola consulta SQL. |

