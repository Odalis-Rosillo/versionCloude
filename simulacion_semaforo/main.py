#!/usr/bin/env python3
"""Punto de entrada: simulación de cola vehicular en un semáforo (DES)."""
import argparse
import sys

from config import ESCENARIOS_DEFECTO, ConfigSimulacion, Escenario
from engine import ejecutar_experimento, obtener_traza
from views import consola


def leer_argumentos() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Simulación DES de cola vehicular en semáforo")
    p.add_argument("--horizonte", type=float, default=3600.0, help="duración de cada réplica (s)")
    p.add_argument("--replicas", type=int, default=30, help="número de réplicas por escenario")
    p.add_argument("--semilla", type=int, default=2024, help="semilla base")
    p.add_argument("--detalle", action="store_true", help="métricas con IC 95 %% por escenario")
    p.add_argument("--traza", type=int, metavar="N", default=0,
                   help="muestra los primeros N eventos de una réplica")
    # Escenario personalizado (si se indica alguno de estos, se usa solo ese)
    p.add_argument("--lam", type=float, help="tasa de llegada λ (veh/s)")
    p.add_argument("--verde", type=float, help="duración del verde g (s)")
    p.add_argument("--rojo", type=float, help="duración del rojo r (s)")
    p.add_argument("--mu", type=float, default=0.5, help="tasa de servicio μ en verde (veh/s)")
    return p.parse_args()


def main() -> int:
    args = leer_argumentos()
    config = ConfigSimulacion(args.horizonte, args.replicas, args.semilla)

    if any(v is not None for v in (args.lam, args.verde, args.rojo)):
        escenarios = [Escenario("Personalizado",
                                lam=args.lam if args.lam is not None else 0.15,
                                verde=args.verde if args.verde is not None else 30,
                                rojo=args.rojo if args.rojo is not None else 30,
                                mu=args.mu)]
    else:
        escenarios = ESCENARIOS_DEFECTO

    consola.encabezado(config)
    resumenes = ejecutar_experimento(escenarios, config)
    consola.tabla_comparativa(resumenes)

    if args.detalle:
        for r in resumenes:
            consola.detalle_escenario(r)
    if args.traza > 0:
        consola.traza(obtener_traza(escenarios[0], config), args.traza)
    return 0


if __name__ == "__main__":
    sys.exit(main())
