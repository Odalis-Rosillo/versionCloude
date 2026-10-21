"""Parámetros de la simulación del acceso semaforizado.

Unidades: tiempos en segundos (s), tasas en vehículos por segundo (veh/s).
Referencia útil: 1800 veh/h = 0.5 veh/s (flujo de saturación típico por carril).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Escenario:
    """Una combinación de demanda y tiempos de fase a evaluar."""
    nombre: str
    lam: float          # tasa de llegadas λ (veh/s), proceso de Poisson
    verde: float        # duración del verde g (s)
    rojo: float         # duración del rojo r (s)
    mu: float = 0.5     # tasa de servicio fija durante el verde (veh/s)

    def __post_init__(self):
        if self.lam < 0:
            raise ValueError("λ no puede ser negativa")
        if self.verde <= 0 or self.rojo <= 0:
            raise ValueError("verde y rojo deben ser > 0")
        if self.mu <= 0:
            raise ValueError("μ debe ser > 0")

    @property
    def ciclo(self) -> float:
        return self.verde + self.rojo

    @property
    def intervalo_servicio(self) -> float:
        """Tiempo que toma atender un vehículo (s/veh) = 1/μ."""
        return 1.0 / self.mu

    @property
    def intensidad(self) -> float:
        """ρ = vehículos que llegan por ciclo / vehículos que se pueden servir por ciclo."""
        return (self.lam * self.ciclo) / (self.mu * self.verde)


@dataclass(frozen=True)
class ConfigSimulacion:
    horizonte: float = 3600.0   # H: duración de cada réplica (s)
    n_replicas: int = 30        # réplicas independientes por escenario
    semilla_base: int = 2024    # réplica i usa la semilla semilla_base + i


# Escenarios por defecto (μ = 0.5 veh/s = 1800 veh/h)
ESCENARIOS_DEFECTO = [
    Escenario("Base        (g=30, r=30, λ=0.15)", lam=0.15, verde=30, rojo=30),
    Escenario("Verde corto (g=20, r=40, λ=0.15)", lam=0.15, verde=20, rojo=40),
    Escenario("Verde largo (g=40, r=20, λ=0.15)", lam=0.15, verde=40, rojo=20),
    Escenario("Demanda alta (g=30, r=30, λ=0.25)", lam=0.25, verde=30, rojo=30),
    Escenario("Sobresaturado (g=30, r=30, λ=0.35)", lam=0.35, verde=30, rojo=30),
]
