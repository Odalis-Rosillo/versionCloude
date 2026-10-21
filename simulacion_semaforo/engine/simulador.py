"""Motor de simulación de eventos discretos (DES) para un acceso semaforizado.

Reglas del modelo:
  * Llegadas: Poisson homogéneo (tiempos entre llegadas ~ Exp(λ)).
  * Servicio: solo en VERDE, determinista, un vehículo cada 1/μ segundos.
  * Un vehículo solo inicia servicio si alcanza a salir antes de que termine
    el verde, así ninguna salida ocurre en rojo.
  * Disciplina FIFO. El vehículo en servicio sigue contando dentro de Q(t)
    hasta que sale.
"""
import heapq
import itertools
import random

from config import Escenario
from models import Cola, Estadisticas, Fase, ResultadoReplica, Semaforo, Vehiculo

from .eventos import Evento, TipoEvento

EPS = 1e-9  # tolerancia numérica para comparar instantes


class Simulador:
    def __init__(self, escenario: Escenario, horizonte: float, semilla: int,
                 registrar_traza: bool = False):
        self.esc = escenario
        self.horizonte = horizonte
        self.semilla = semilla
        self.rng = random.Random(semilla)   # generador propio → reproducible

        self.semaforo = Semaforo(escenario.verde, escenario.rojo)
        self.cola = Cola()
        self.stats = Estadisticas(registrar_traza)

        self.t = 0.0
        self._agenda = []                   # heap de eventos
        self._seq = itertools.count()
        self._servidor_ocupado = False
        self._atendidos_ciclo = 0
        self._contador_veh = 0

    # ------------------------------------------------------------ agenda
    def _programar(self, tiempo: float, tipo: TipoEvento) -> None:
        heapq.heappush(self._agenda, Evento(tiempo, tipo, next(self._seq)))

    def _programar_llegada(self) -> None:
        dt = self.rng.expovariate(self.esc.lam)
        self._programar(self.t + dt, TipoEvento.LLEGADA)

    # ------------------------------------------------------- bucle principal
    def ejecutar(self) -> ResultadoReplica:
        self._programar(self.semaforo.fin_fase_actual(), TipoEvento.CAMBIO_FASE)
        if self.esc.lam > 0:
            self._programar_llegada()

        while self._agenda:
            evento = heapq.heappop(self._agenda)
            if evento.tiempo > self.horizonte:
                break
            self.t = evento.tiempo
            if evento.tipo is TipoEvento.LLEGADA:
                self._on_llegada()
            elif evento.tipo is TipoEvento.SALIDA:
                self._on_salida()
            else:
                self._on_cambio_fase()

        self.cola.cerrar(self.horizonte)
        return self.stats.consolidar(self.cola, self.horizonte, self.semilla)

    # --------------------------------------------------------------- manejadores
    def _on_llegada(self) -> None:
        self._contador_veh += 1
        veh = Vehiculo(self._contador_veh, self.t, self.semaforo.ciclo)
        self.cola.encolar(veh, self.t)
        self.stats.registrar_llegada()
        self.stats.registrar_evento(self.t, "LLEGADA", self.semaforo.fase.value,
                                    len(self.cola), f"veh {veh.id}")
        self._programar_llegada()
        self._intentar_servicio()

    def _on_salida(self) -> None:
        veh = self.cola.desencolar(self.t)
        veh.t_salida = self.t
        self._servidor_ocupado = False
        self._atendidos_ciclo += 1
        self.stats.registrar_salida(veh)
        self.stats.registrar_evento(self.t, "SALIDA", self.semaforo.fase.value,
                                    len(self.cola),
                                    f"veh {veh.id} (demora {veh.demora:.1f} s)")
        self._intentar_servicio()

    def _on_cambio_fase(self) -> None:
        if self.semaforo.fase is Fase.VERDE:
            # Termina un verde: registrar vehículos atendidos y cola residual
            self.stats.cerrar_verde(self._atendidos_ciclo, len(self.cola))

        nueva = self.semaforo.avanzar(self.t)
        self.stats.registrar_evento(self.t, "FASE", nueva.value, len(self.cola),
                                    f"→ {nueva.value}")
        self._programar(self.semaforo.fin_fase_actual(), TipoEvento.CAMBIO_FASE)

        if nueva is Fase.VERDE:
            self._atendidos_ciclo = 0
            self._intentar_servicio()

    # ------------------------------------------------------------------ servicio
    def _intentar_servicio(self) -> None:
        """Inicia el servicio del primer vehículo si las condiciones lo permiten."""
        if self._servidor_ocupado or not self.semaforo.permite_paso or len(self.cola) == 0:
            return
        fin_verde = self.semaforo.fin_fase_actual()
        t_salida = self.t + self.esc.intervalo_servicio
        if t_salida > fin_verde + EPS:
            return  # no alcanza a cruzar antes del rojo
        self._servidor_ocupado = True
        self._programar(min(t_salida, fin_verde), TipoEvento.SALIDA)
