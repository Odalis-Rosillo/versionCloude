"""Cola FIFO que además integra el área bajo Q(t) para la longitud media."""
from collections import deque
from typing import List

from .vehiculo import Vehiculo


class Cola:
    def __init__(self):
        self._fila = deque()
        self._t_ultimo = 0.0   # instante de la última actualización del área
        self.area = 0.0        # ∫ Q(t) dt acumulada
        self.maximo = 0        # Q_max observada

    def __len__(self) -> int:
        return len(self._fila)

    def _acumular(self, t: float) -> None:
        # Q(t) es constante entre eventos: área += Q * Δt
        self.area += len(self._fila) * (t - self._t_ultimo)
        self._t_ultimo = t

    def encolar(self, vehiculo: Vehiculo, t: float) -> None:
        self._acumular(t)
        self._fila.append(vehiculo)
        self.maximo = max(self.maximo, len(self._fila))

    def desencolar(self, t: float) -> Vehiculo:
        self._acumular(t)
        return self._fila.popleft()

    def cerrar(self, t: float) -> None:
        """Cierra la integral al final del horizonte."""
        self._acumular(t)

    def vehiculos(self) -> List[Vehiculo]:
        return list(self._fila)
