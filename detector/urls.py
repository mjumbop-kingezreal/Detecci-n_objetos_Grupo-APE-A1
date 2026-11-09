from django.urls import path
from . import views

app_name = "detector"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("video/", views.video, name="video"),
    path("detener/", views.detener, name="detener"),
    path("estado/", views.estado, name="estado"),
    path("guardar/", views.guardar, name="guardar"),
    path("historial/", views.historial, name="historial"),
]
