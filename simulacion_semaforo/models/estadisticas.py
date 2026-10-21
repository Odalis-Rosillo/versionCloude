"""Recolección de datos y cálculo de métricas de una réplica."""
from collections import namedtuple
from dataclasses import dataclass
from statistics import mean
from typing import List

RegistroEvento = namedtuple("RegistroEvento", "t tipo fase cola detalle")


@dataclass
class ResultadoReplica:
    """Métricas de una réplica (una corrida con una semilla)."""
    semilla: int
    llegadas: int
    atendidos: int
    pendientes_final: int          # vehículos aún en cola al terminar el horizonte
    long_media: float              # L̄q = (1/H) ∫ Q(t) dt
    long_max: int                  # Q_max
    demora_media: float            # solo vehículos que salieron
    demora_media_censurada: float  # incluye pendientes (demora hasta H)
    residual_medio: float          # cola residual media al terminar el verde
    residual_max: int
    atendidos_por_ciclo: float
    ciclos_completos: int


class Estadisticas:
    def __init__(self, registrar_traza: bool = False):
        self.registrar_traza = registrar_traza
        self.traza: List[RegistroEvento] = []
        self.llegadas = 0
        self.demoras: List[float] = []
        self.atendidos_por_ciclo: List[int] = []
        self.residual_por_ciclo: List[int] = []

    def registrar_evento(self, t, tipo, fase, longitud_cola, detalle="") -> None:
        if self.registrar_traza:
            self.traza.append(RegistroEvento(t, tipo, fase, longitud_cola, detalle))

    def registrar_llegada(self) -> None:
        self.llegadas += 1

    def registrar_salida(self, vehiculo) -> None:
        self.demoras.append(vehiculo.demora)

    def cerrar_verde(self, atendidos: int, residual: int) -> None:
        """Se llama justo cuando termina un verde."""
        self.atendidos_por_ciclo.append(atendidos)
        self.residual_por_ciclo.append(residual)

    @staticmethod
    def _media(valores) -> float:
        return mean(valores) if valores else 0.0

    def consolidar(self, cola, horizonte: float, semilla: int) -> ResultadoReplica:
        pendientes = cola.vehiculos()
        # Los pendientes aportan su espera acumulada hasta H (demora censurada)
        demoras_cens = self.demoras + [horizonte - v.t_llegada for v in pendientes]
        return ResultadoReplica(
            semilla=semilla,
            llegadas=self.llegadas,
            atendidos=len(self.demoras),
            pendientes_final=len(pendientes),
            long_media=cola.area / horizonte,
            long_max=cola.maximo,
            demora_media=self._media(self.demoras),
            demora_media_censurada=self._media(demoras_cens),
            residual_medio=self._media(self.residual_por_ciclo),
            residual_max=max(self.residual_por_ciclo, default=0),
            atendidos_por_ciclo=self._media(self.atendidos_por_ciclo),
            ciclos_completos=len(self.residual_por_ciclo),
        )
