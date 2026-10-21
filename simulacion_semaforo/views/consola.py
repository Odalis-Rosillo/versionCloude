"""Vista de consola: solo formatea e imprime, no calcula nada del modelo."""
from typing import List

ANCHO = 112


def _linea(car: str = "=") -> str:
    return car * ANCHO


def encabezado(config) -> None:
    print(_linea())
    print("  SIMULACIÓN DE COLA VEHICULAR EN SEMÁFORO (eventos discretos)")
    print(_linea())
    print(f"  Horizonte H = {config.horizonte:.0f} s | Réplicas = {config.n_replicas} "
          f"| Semilla base = {config.semilla_base}")
    print()


def tabla_comparativa(resumenes: List) -> None:
    cols = ("{:<36}{:>6}{:>9}{:>8}{:>10}{:>11}{:>14}{:>11}{:>9}")
    print(cols.format("Escenario", "ρ", "L̄q", "Qmáx", "W (s)", "W cens.(s)",
                      "Resid.medio", "Resid.máx", "Atend/c"))
    print(_linea("-"))
    for r in resumenes:
        e = r.escenario
        print(cols.format(
            e.nombre[:36],
            f"{e.intensidad:.2f}",
            f"{r.estadistico('long_media')[0]:.2f}",
            f"{r.estadistico('long_max')[0]:.1f}",
            f"{r.estadistico('demora_media')[0]:.1f}",
            f"{r.estadistico('demora_media_censurada')[0]:.1f}",
            f"{r.estadistico('residual_medio')[0]:.2f}",
            f"{r.estadistico('residual_max')[0]:.1f}",
            f"{r.estadistico('atendidos_por_ciclo')[0]:.1f}",
        ))
    print(_linea("-"))
    print("  L̄q: longitud media temporal | Qmáx: longitud máxima | W: demora media (solo salidas)")
    print("  W cens.: demora incluyendo vehículos aún en cola al final | Resid.: cola al terminar el verde")
    print("  Atend/c: vehículos atendidos por ciclo | ρ = λ·T / (μ·g)  (ρ ≥ 1 → cola crece sin límite)")
    print("  Valores = media de las réplicas.")
    print()


def detalle_escenario(resumen) -> None:
    e = resumen.escenario
    print(_linea("-"))
    print(f"  {e.nombre}")
    print(f"  λ={e.lam} veh/s | g={e.verde} s | r={e.rojo} s | T={e.ciclo} s | "
          f"μ={e.mu} veh/s | ρ={e.intensidad:.2f}")
    print(_linea("-"))
    filas = [
        ("Longitud media de cola L̄q (veh)", "long_media", "{:.3f}"),
        ("Longitud máxima Qmáx (veh)", "long_max", "{:.2f}"),
        ("Demora media W (s/veh)", "demora_media", "{:.2f}"),
        ("Demora media censurada (s/veh)", "demora_media_censurada", "{:.2f}"),
        ("Cola residual media al fin del verde", "residual_medio", "{:.2f}"),
        ("Cola residual máxima al fin del verde", "residual_max", "{:.2f}"),
        ("Vehículos atendidos por ciclo", "atendidos_por_ciclo", "{:.2f}"),
        ("Vehículos llegados (total)", "llegadas", "{:.1f}"),
        ("Vehículos pendientes al final", "pendientes_final", "{:.1f}"),
    ]
    for etiqueta, attr, fmt in filas:
        m, s, ic = resumen.estadistico(attr)
        print(f"  {etiqueta:<42}{fmt.format(m):>10}  ± {ic:<8.3f} (s={s:.3f})")
    print("  (± = semiancho del IC 95 %)")
    print()


def traza(registros, limite: int) -> None:
    print(_linea())
    print(f"  TRAZA DE EVENTOS (primeros {limite})")
    print(_linea())
    print(f"  {'t (s)':>9}  {'Evento':<8}{'Fase':<7}{'Q':>4}  Detalle")
    for r in registros[:limite]:
        print(f"  {r.t:>9.2f}  {r.tipo:<8}{r.fase:<7}{r.cola:>4}  {r.detalle}")
    print()
