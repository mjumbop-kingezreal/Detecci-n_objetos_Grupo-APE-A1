from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Deteccion(models.Model):
    objeto = models.CharField(max_length=100)

    confianza = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(1),
        ]
    )

    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Detección"
        verbose_name_plural = "Detecciones"

    @property
    def porcentaje(self):
        return round(self.confianza * 100, 1)

    def __str__(self):
        return f"{self.objeto}: {self.porcentaje}%"