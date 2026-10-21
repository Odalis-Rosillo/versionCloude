"""Entidad Vehiculo: guarda sus instantes de llegada y salida."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Vehiculo:
    id: int
    t_llegada: float
    ciclo_llegada: int
    t_salida: Optional[float] = None

    @property
    def demora(self) -> Optional[float]:
        """Tiempo en el sistema (llegada → salida). None si aún está en cola."""
        if self.t_salida is None:
            return None
        return self.t_salida - self.t_llegada
