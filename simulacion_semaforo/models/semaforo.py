"""Semáforo de dos fases (ROJO / VERDE) con ciclo fijo.

Esta versión inicial no modela el amarillo/despeje; se puede agregar como
una tercera fase más adelante.
"""
from enum import Enum


class Fase(Enum):
    ROJO = "ROJO"
    VERDE = "VERDE"


class Semaforo:
    def __init__(self, verde: float, rojo: float, fase_inicial: Fase = Fase.ROJO):
        if verde <= 0 or rojo <= 0:
            raise ValueError("Las duraciones de verde y rojo deben ser > 0")
        self.verde = verde
        self.rojo = rojo
        self.fase = fase_inicial
        self.t_inicio_fase = 0.0
        self.ciclo = 0                      # índice del ciclo actual
        self._fase_inicial = fase_inicial   # al volver a ella empieza un nuevo ciclo

    @property
    def permite_paso(self) -> bool:
        return self.fase is Fase.VERDE

    def duracion_fase_actual(self) -> float:
        return self.verde if self.fase is Fase.VERDE else self.rojo

    def fin_fase_actual(self) -> float:
        return self.t_inicio_fase + self.duracion_fase_actual()

    def avanzar(self, t: float) -> Fase:
        """Cambia de fase en el instante t y devuelve la nueva fase."""
        self.fase = Fase.VERDE if self.fase is Fase.ROJO else Fase.ROJO
        self.t_inicio_fase = t
        if self.fase is self._fase_inicial:
            self.ciclo += 1
        return self.fase
