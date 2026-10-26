# Esquema de `modelo.json`

Entrada de [`scripts/fin_model.py`](../scripts/fin_model.py). Plantilla completa y ejecutable: [`scripts/ejemplo_modelo.json`](../scripts/ejemplo_modelo.json) — cópiala y edítala en vez de escribir desde cero.

```bash
python <AgentGarden>/.agents/skills/finantial-analysis/scripts/fin_model.py modelo.json --out resultados.json --csv flujos.csv --md resumen.md
```

Opcionales: `--sims 5000` (simulaciones Monte Carlo), `--seed 42` (misma semilla ⇒ mismo resultado).

## Nivel raíz (envolvente de decisión)

| Campo | Oblig. | Significado |
|---|---|---|
| `horizonte_meses` | sí | Igual para todas las candidatas. Mes 0 = inversión inicial. |
| `tasa_descuento_anual` | sí | Costo de oportunidad del capital (ej. `0.14`). Se convierte a mensual compuesta. |
| `candidatas` | sí | Lista de candidatas (abajo). La **opción cero** la agrega el script; no la declares. |
| `moneda` | no | Default `CLP`. Todo el modelo en una sola moneda y en montos **netos sin IVA**. |
| `tasa_impuesto` | no | Sobre resultado operativo positivo, con arrastre de pérdidas. Default 0 (antes de impuestos). |
| `valor_hora_fundador` | no | Costo de oportunidad de una hora del fundador. Resta al flujo económico, no a la caja. |
| `capital_disponible` | no | Filtro: exposición de caja P90 debe caber aquí. |
| `perdida_maxima_tolerable` | no | Filtro: pérdida de caja del camino de fallo debe caber aquí. |
| `horas_disponibles_mes` | no | Filtro: `horas_fundador_mes` de cada candidata debe caber aquí. |
| `criterio_ranking` | no | `valor_esperado` (default), `valor_esperado_por_peso` (capital escaso), `p_mejor`. |
| `escenarios` | no | Sobrescribe multiplicadores globales `pesimista`/`optimista` por driver. |

## Candidata

| Campo | Significado |
|---|---|
| `id`, `nombre` | Identificador corto único y nombre legible. |
| `horas_fundador_mes` | Horas/mes que exige del fundador o equipo no remunerado. |
| `p_exito` | Probabilidad de **superar el criterio de muerte** en `mes_corte`. Default 1.0 (alerta). |
| `mes_corte` | Mes en que se evalúa el criterio de muerte (fin del MKI). |
| `recupero_fallo` | Fracción del capex gastado hasta el corte que se recupera al liquidar (reventa, stock). |
| `puntuales` | Montos únicos `{concepto, mes, monto, tipo}`. Negativo = salida. `tipo: "capex"` escala con el driver `inversion` y entra al recupero; otros tipos (`capital_trabajo`, `subsidio`, `otro`) no. |
| `lineas_ingreso` | Ver abajo. |
| `costos_fijos` | `{concepto, monto_mes, mes_inicio, mes_fin?}`. `mes_fin` default = horizonte. |
| `valor_terminal` | Monto al final del horizonte en el camino de éxito. Default 0; justifícalo si lo usas. |
| `rangos` | `{driver: [mult_pesimista, mult_optimista]}` para esta candidata. |

### Líneas de ingreso

| Campo | `transaccional` | `recurrente` |
|---|---|---|
| volumen inicial | `unidades_mes` | `altas_mes` (nuevos clientes/mes) |
| `crecimiento_mensual` | crecimiento compuesto de unidades | crecimiento compuesto de altas |
| `tope_unidades` | techo de unidades/mes (capacidad o mercado) | techo de altas/mes |
| `churn_mensual` | — | fracción de la base activa que se va cada mes |
| `cac` | — (inclúyelo en `costo_variable`) | costo de adquisición por alta |
| `precio`, `costo_variable` | por unidad | por cliente activo al mes |
| `mes_inicio` | primer mes con ventas (default 1) | ídem |

Cómo modelar otros tipos de idea con estas piezas:

- **Ahorro interno / automatización**: línea `transaccional` con `precio` = costo evitado por unidad (hora, envío, error) y `costo_variable` = costo marginal que queda.
- **Servicio con capacidad limitada**: `tope_unidades` = capacidad física (horas, cupos, máquinas).
- **Inventario / capital de trabajo**: `puntuales` con `tipo: "capital_trabajo"` al comprar y monto positivo al liquidar si aplica.
- **Subsidio o fondo concursable** (CORFO, Sercotec): `puntuales` positivo con `tipo: "subsidio"` — solo si está adjudicado; si no, modélalo como candidata aparte o como escenario.
- **Prototipo por Marks**: capex del MKI en mes 0, capex del MKII **después** de `mes_corte`. El camino de fallo no gasta el MKII: así el modelo premia escalonar la apuesta.

## Drivers y escenarios

Drivers: `volumen`, `precio`, `costo_variable`, `costos_fijos`, `inversion`, `crecimiento`, `churn`. Cada uno es un multiplicador sobre la base (1.0).

| Driver | Pesimista | Optimista |
|---|---|---|
| volumen | 0.6 | 1.3 |
| precio | 0.9 | 1.05 |
| costo_variable | 1.1 | 0.95 |
| costos_fijos | 1.15 | 0.95 |
| inversion | 1.3 | 1.0 |
| crecimiento | 0.5 | 1.3 |
| churn | 1.5 | 0.8 |

Los defaults son **asimétricos a propósito**: corrigen el sesgo optimista (la inversión casi nunca sale más barata, el volumen decepciona más de lo que sorprende). Sobrescribe con `rangos` cuando el libro de supuestos tenga evidencia de un rango distinto — no para mejorar el resultado.

## Semántica de las salidas

- **Flujo económico vs. caja**: el económico descuenta el tiempo imputado del fundador (VAN, TIR, payback); la caja es lo que sale del bolsillo (exposición, pérdida si falla).
- **Camino de fallo**: escenario pesimista hasta `mes_corte`, luego liquidación con `recupero_fallo`. Ocurre con probabilidad `1 − p_exito` en el Monte Carlo.
- **Valor esperado**: media del Monte Carlo (fallo + incertidumbre triangular por driver). Es la cifra que ordena el ranking; el VAN base es la moda, no la media.
- **Exposición de caja P90**: capital que hay que tener para no quedarse sin caja en 9 de cada 10 mundos simulados.
- **P(mejor)**: fracción de simulaciones en que la candidata gana a todas las demás **y a la opción cero**.
- **Supuesto crítico**: driver con mayor swing de VAN en el tornado.
- **Valor de quiebre**: multiplicador del driver que lleva el VAN base a 0. Tradúcelo a unidades reales (×0.68 sobre 8 ventas/mes = 5,4 ventas/mes).
- **Alertas**: supuestos faltantes o sospechosos. Cada una se corrige en el modelo o se acepta explícitamente en `supuestos.md`.

Simplificaciones conocidas (decláralas en el informe si pesan): sin depreciación tributaria del capex (sobreestima impuestos, conservador), drivers independientes en el Monte Carlo, crecimiento compuesto sin estacionalidad.
