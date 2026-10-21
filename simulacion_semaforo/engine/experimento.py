"""Controlador del experimento: corre las réplicas y agrega resultados."""
from dataclasses import dataclass
from statistics import mean, stdev
from typing import List, Tuple

from config import ConfigSimulacion, Escenario
from models import ResultadoReplica

from .simulador import Simulador

# Valores t de Student (bilateral 95 %) para 1..30 grados de libertad
_T95 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228,
        2.201, 2.179, 2.160, 2.145, 2.131, 2.120, 2.110, 2.101, 2.093, 2.086,
        2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


@dataclass
class ResumenEscenario:
    escenario: Escenario
    replicas: List[ResultadoReplica]

    def estadistico(self, atributo: str) -> Tuple[float, float, float]:
        """Devuelve (media, desviación estándar, semiancho del IC 95 %)."""
        valores = [getattr(r, atributo) for r in self.replicas]
        n = len(valores)
        m = mean(valores)
        if n < 2:
            return m, 0.0, 0.0
        s = stdev(valores)
        t = _T95[n - 2] if n - 1 <= len(_T95) else 1.96
        return m, s, t * s / n ** 0.5


def ejecutar_escenario(escenario: Escenario, config: ConfigSimulacion) -> ResumenEscenario:
    # Misma semilla para la réplica i en todos los escenarios → comparación más justa
    replicas = [
        Simulador(escenario, config.horizonte, config.semilla_base + i).ejecutar()
        for i in range(config.n_replicas)
    ]
    return ResumenEscenario(escenario, replicas)


def ejecutar_experimento(escenarios: List[Escenario],
                         config: ConfigSimulacion) -> List[ResumenEscenario]:
    return [ejecutar_escenario(e, config) for e in escenarios]


def obtener_traza(escenario: Escenario, config: ConfigSimulacion):
    """Corre una sola réplica con traza de eventos (para depurar/validar)."""
    sim = Simulador(escenario, config.horizonte, config.semilla_base, registrar_traza=True)
    sim.ejecutar()
    return sim.stats.traza
