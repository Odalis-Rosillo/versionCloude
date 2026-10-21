"""Eventos de la simulación y su orden en la agenda."""
from dataclasses import dataclass, field
from enum import IntEnum


class TipoEvento(IntEnum):
    # El valor numérico desempata eventos simultáneos:
    # primero salidas, luego cambio de fase, luego llegadas.
    SALIDA = 0
    CAMBIO_FASE = 1
    LLEGADA = 2


@dataclass(order=True)
class Evento:
    tiempo: float
    tipo: TipoEvento
    seq: int = field(compare=True)   # orden de creación: desempate estable
