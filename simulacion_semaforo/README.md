# Simulación de cola vehicular en un semáforo (eventos discretos)

Proyecto de **Teoría de Colas** – Computación, Universidad Nacional de Loja.
Simula un acceso semaforizado como un sistema de cola: llegadas de Poisson,
servicio solo en verde con tasa fija y acumulación estricta en rojo.

## Requisitos

- Linux (o cualquier sistema con terminal)
- Python 3.9 o superior
- Sin dependencias externas (solo biblioteca estándar)

Verifica tu versión de Python:

```bash
python3 --version
```

## Ejecución rápida

```bash
unzip simulacion_semaforo.zip
cd simulacion_semaforo
python3 main.py
```

Esto corre los 5 escenarios por defecto con 30 réplicas de 3600 s cada uno e
imprime una tabla comparativa.

## Opciones de línea de comandos

| Opción | Descripción | Por defecto |
|---|---|---|
| `--horizonte H` | Duración de cada réplica (s) | 3600 |
| `--replicas N` | Réplicas por escenario | 30 |
| `--semilla S` | Semilla base (réplica *i* usa `S+i`) | 2024 |
| `--detalle` | Métricas con desviación e IC 95 % por escenario | desactivado |
| `--traza N` | Muestra los primeros N eventos de una réplica | desactivado |
| `--lam L` | Tasa de llegada λ (veh/s) | 0.15 |
| `--verde G` | Duración del verde g (s) | 30 |
| `--rojo R` | Duración del rojo r (s) | 30 |
| `--mu M` | Tasa de servicio μ en verde (veh/s) | 0.5 |

Si se indica `--lam`, `--verde` o `--rojo`, se simula **solo** ese escenario
personalizado en lugar de los 5 por defecto.

### Ejemplos

```bash
# Métricas detalladas con intervalos de confianza
python3 main.py --detalle

# Ver la secuencia de eventos (llegadas, cambios de fase, salidas)
python3 main.py --traza 25

# Escenario propio: λ = 0.2 veh/s, verde 35 s, rojo 25 s, 50 réplicas
python3 main.py --lam 0.2 --verde 35 --rojo 25 --replicas 50

# Corrida larga y reproducible
python3 main.py --horizonte 7200 --semilla 123
```

## Pruebas

```bash
python3 -m unittest discover -s tests -t .
```

Cubren los casos controlados de la metodología: sin llegadas (λ=0), verde
insuficiente, demanda alta, conservación de vehículos, ausencia de salidas en
rojo, capacidad por ciclo y reproducibilidad por semilla.

## Estructura del proyecto

```
simulacion_semaforo/
├── main.py              # punto de entrada (CLI)
├── config.py            # parámetros y escenarios por defecto
├── requirements.txt     # solo stdlib
├── models/              # dominio: Vehiculo, Semaforo, Cola, Estadisticas
├── engine/              # motor DES, eventos y controlador del experimento
├── views/               # salida de consola
└── tests/               # pruebas unitarias
```

Para cambiar los escenarios o parámetros fijos, edita `config.py`.

## Métricas que reporta

| Métrica | Significado |
|---|---|
| ρ | λ·T / (μ·g). Si ρ ≥ 1 la cola crece sin límite |
| L̄q | Longitud media temporal de cola: (1/H) ∫ Q(t) dt |
| Qmáx | Longitud máxima de cola |
| W | Demora media por vehículo (solo los que salieron) |
| W cens. | Demora media incluyendo los vehículos que siguen en cola al final |
| Resid. medio / máx | Vehículos en cola al terminar cada verde |
| Atend/c | Vehículos atendidos por ciclo |

## Supuestos del modelo

- Un solo acceso y una sola cola, disciplina FIFO.
- Llegadas Poisson homogéneas (tiempos entre llegadas exponenciales).
- Servicio determinista: un vehículo cada 1/μ s, solo durante el verde.
- Un vehículo solo inicia servicio si alcanza a salir antes de que acabe el verde.
- Sin fase de amarillo/despeje (pendiente).
- La simulación inicia en rojo con la cola vacía, sin período de calentamiento.
- Los resultados describen el sistema simulado; no equivalen a datos de campo.
