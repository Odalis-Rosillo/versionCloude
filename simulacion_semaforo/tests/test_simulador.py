"""Casos controlados mencionados en la metodología (paso 8)."""
import unittest

from config import Escenario
from engine import Simulador


class PruebasSimulador(unittest.TestCase):
    def test_sin_llegadas(self):
        r = Simulador(Escenario("l0", 0.0, 30, 30), 600, 1).ejecutar()
        self.assertEqual((r.llegadas, r.atendidos, r.long_max), (0, 0, 0))

    def test_verde_insuficiente_no_atiende(self):
        # g=1 s < 1/μ=2 s: nadie alcanza a cruzar, la cola solo crece
        r = Simulador(Escenario("g_corto", 0.2, 1, 30, mu=0.5), 600, 1).ejecutar()
        self.assertEqual(r.atendidos, 0)
        self.assertEqual(r.pendientes_final, r.llegadas)

    def test_conservacion_de_vehiculos(self):
        r = Simulador(Escenario("alta", 0.35, 30, 30), 1800, 7).ejecutar()
        self.assertEqual(r.llegadas, r.atendidos + r.pendientes_final)
        self.assertGreater(r.pendientes_final, 0)  # demanda deliberadamente alta

    def test_sin_salidas_en_rojo(self):
        sim = Simulador(Escenario("x", 0.2, 30, 30), 1200, 3, registrar_traza=True)
        sim.ejecutar()
        for reg in sim.stats.traza:
            if reg.tipo == "SALIDA":
                self.assertEqual(reg.fase, "VERDE")

    def test_capacidad_por_ciclo(self):
        # Demanda muy alta: se atienden g·μ = 15 vehículos por ciclo
        r = Simulador(Escenario("sat", 1.0, 30, 30, mu=0.5), 1800, 5).ejecutar()
        self.assertAlmostEqual(r.atendidos_por_ciclo, 15.0, delta=0.5)

    def test_reproducible(self):
        e = Escenario("rep", 0.15, 30, 30)
        a = Simulador(e, 900, 42).ejecutar()
        b = Simulador(e, 900, 42).ejecutar()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
