from django.test import SimpleTestCase, TestCase
from detector.views import clave_estado
from detector.models import Deteccion


# PRUEBA UNITARIA
class PruebaUnitaria(SimpleTestCase):

    def test_clave_estado(self):
        resultado = clave_estado("sesion123")

        self.assertEqual(
            resultado,
            "deteccion:estado:sesion123"
        )


# PRUEBAS DE INTEGRACION
class PruebasIntegracion(TestCase):

    def test_pagina_principal(self):
        respuesta = self.client.get("/")

        self.assertEqual(respuesta.status_code, 200)

    def test_guardar_en_postgresql(self):
        Deteccion.objects.create(
            objeto="Botella",
            confianza=0.95
        )

        self.assertEqual(Deteccion.objects.count(), 1)
