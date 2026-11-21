"""Detección local con YOLO-World y guardado manual en PostgreSQL.

La cámara pertenece al equipo que ejecuta Django. Esta etapa usa runserver,
un proceso y una transmisión activa. El historial es común al proyecto.
"""
from functools import lru_cache
import logging
from threading import Event, Lock
from time import time
from uuid import uuid4

import cv2
from ultralytics import YOLOWorld

from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_POST

from .models import Deteccion

logger = logging.getLogger(__name__)
CAMARA_LIBRE = Lock()
ESTADO_LOCK = Lock()
GUARDADO_LOCK = Lock()
TRANSMISIONES = {}
OBJETOS = [
    ("person", "Persona"), ("bottle", "Botella"),
    ("cell phone", "Celular"), ("apple", "Manzana"),
    ("computer mouse", "Mouse"), ("eyeglasses", "Lentes"),
    ("medical face mask", "Mascarilla"), ("shoe", "Zapato"),
    ("keyboard", "Teclado"), ("laptop", "Laptop"),
    ("book", "Libro"), ("chair", "Silla"),
]
NOMBRES = dict(enumerate(nombre for _, nombre in OBJETOS))


def clave_estado(sesion):
    return f"deteccion:estado:{sesion}"


@lru_cache(maxsize=1)
def obtener_modelo():
    modelo = YOLOWorld(str(settings.BASE_DIR / "yolov8s-worldv2.pt"))
    modelo.set_classes([texto for texto, _ in OBJETOS])
    return modelo


@require_GET
@never_cache
def inicio(request):
    # Crea una sesión para asociar el último resultado a este navegador.
    request.session.setdefault("detector_iniciado", True)
    return render(request, "detector/inicio.html")


def limpiar_transmision(sesion, evento, camara=None):
    with ESTADO_LOCK:
        if TRANSMISIONES.get(sesion) is evento:
            try:
                if camara is not None:
                    camara.release()
            finally:
                CAMARA_LIBRE.release()
                TRANSMISIONES.pop(sesion, None)
                cache.delete(clave_estado(sesion))


class RespuestaVideo(StreamingHttpResponse):
    def __init__(self, contenido, sesion, evento, camara):
        super().__init__(
            contenido, content_type="multipart/x-mixed-replace; boundary=frame",
        )
        self.sesion, self.evento, self.camara = sesion, evento, camara

    def close(self):
        try:
            super().close()
        finally:
            # También libera si el navegador cierra antes del primer fotograma.
            limpiar_transmision(self.sesion, self.evento, self.camara)


def generar_video(camara, modelo, sesion, evento):
    try:
        while not evento.is_set():
            correcto, imagen = camara.read()
            if not correcto:
                logger.warning("No se pudo leer la cámara.")
                break
            resultado = modelo.predict(
                imagen, imgsz=320, conf=0.25, device="cpu", verbose=False,
            )[0]
            resultado.names = NOMBRES
            filas = [
                {"objeto": NOMBRES[int(clase)], "confianza": float(confianza)}
                for clase, confianza in zip(
                    resultado.boxes.cls.tolist(), resultado.boxes.conf.tolist(),
                )
            ]
            # Se guarda solo en memoria. La BD se escribe al pulsar Guardar.
            with ESTADO_LOCK:
                if evento.is_set():
                    break
                cache.set(clave_estado(sesion), {
                    "activo": True, "fotograma": uuid4().hex,
                    "actualizado": time(), "detecciones": filas,
                }, timeout=15)
            correcto, buffer = cv2.imencode(
                ".jpg", resultado.plot(), [cv2.IMWRITE_JPEG_QUALITY, 75],
            )
            if correcto:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
                       + buffer.tobytes() + b"\r\n")
    finally:
        limpiar_transmision(sesion, evento, camara)


@require_GET
@never_cache
def video(request):
    sesion = request.session.session_key
    if not sesion:
        return HttpResponse("Recarga la página principal.", status=400)
    if not CAMARA_LIBRE.acquire(blocking=False):
        return HttpResponse("La cámara ya está en uso. Detén la otra transmisión.", status=409)
    evento = Event()
    camara = None
    with ESTADO_LOCK:
        TRANSMISIONES[sesion] = evento
        cache.delete(clave_estado(sesion))
    try:
        modelo = obtener_modelo()
        if evento.is_set():
            limpiar_transmision(sesion, evento)
            return HttpResponse("Inicio cancelado.", status=409)
        indice_camara = int(request.GET.get("camara", 0))
        camara = cv2.VideoCapture(indice_camara)
        if not camara.isOpened():
            raise RuntimeError("No se pudo abrir la cámara.")
    except Exception:
        logger.exception("No se pudo iniciar la detección.")
        limpiar_transmision(sesion, evento, camara)
        return HttpResponse("No se pudo iniciar. Revisa la terminal de Django.", status=503)
    return RespuestaVideo(
        generar_video(camara, modelo, sesion, evento),
        sesion, evento, camara,
    )


@require_POST
@never_cache
def detener(request):
    sesion = request.session.session_key
    with ESTADO_LOCK:
        evento = TRANSMISIONES.get(sesion)
        if evento is not None:
            evento.set()
        if sesion:
            cache.delete(clave_estado(sesion))
        detenido = evento is None
    return JsonResponse({
        "detenido": detenido,
        "mensaje": "Detección detenida." if detenido else "Liberando la cámara…",
    })


@require_GET
@never_cache
def estado(request):
    sesion = request.session.session_key
    datos = cache.get(clave_estado(sesion)) if sesion else None
    reciente = bool(datos and time() - datos["actualizado"] <= 5)
    filas = datos["detecciones"] if reciente else []
    return JsonResponse({"listo": reciente, "cantidad": len(filas)})


@require_POST
@never_cache
def guardar(request):
    sesion = request.session.session_key
    if not sesion:
        return JsonResponse({"error": "Recarga la página e inicia la cámara."}, status=409)
    if not GUARDADO_LOCK.acquire(blocking=False):
        return JsonResponse({"error": "Hay un guardado en curso. Espera un momento."}, status=409)
    try:
        # Solo se bloquea el video mientras se copia el resultado en memoria.
        with ESTADO_LOCK:
            datos = cache.get(clave_estado(sesion))
        if not datos or time() - datos["actualizado"] > 5:
            return JsonResponse({"error": "Espera a recibir una detección actual."}, status=409)
        filas = datos["detecciones"]
        if not filas:
            return JsonResponse({"error": "No hay objetos detectados para guardar."}, status=409)
        clave_guardado = f"deteccion:guardado:{sesion}"
        if cache.get(clave_guardado) == datos["fotograma"]:
            return JsonResponse({"error": "Ese fotograma ya fue guardado."}, status=409)
        with transaction.atomic():
            Deteccion.objects.bulk_create([
                Deteccion(objeto=fila["objeto"], confianza=fila["confianza"])
                for fila in filas
            ])
        cache.set(clave_guardado, datos["fotograma"], timeout=600)
    except DatabaseError:
        logger.exception("No se pudieron guardar las detecciones.")
        return JsonResponse({"error": "No se pudo guardar. Revisa la conexión a PostgreSQL e inténtalo otra vez."}, status=503)
    finally:
        GUARDADO_LOCK.release()
    return JsonResponse({"mensaje": f"Se guardaron {len(filas)} detecciones.", "cantidad": len(filas)})


@require_GET
@never_cache
def historial(request):
    filas = Deteccion.objects.order_by("-fecha", "-id")[:50]
    return JsonResponse({
        "total": Deteccion.objects.count(),
        "registros": [
            {"id": fila.id, "objeto": fila.objeto,
             "confianza": fila.porcentaje, "fecha": fila.fecha.isoformat()}
            for fila in filas
        ],
    })
