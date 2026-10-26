# Criterios de decisión y trampas

Consulta en el paso 2 (tasa, `p_exito`, trampas de supuestos) y en el paso 5 (qué métrica manda, lente cualitativa, carteras no excluyentes).

## Tasa de descuento

La tasa es el **costo de oportunidad**: lo que rendiría el mismo dinero en la mejor alternativa accesible (depósito a plazo, fondo conservador, prepagar deuda cara). Busca la tasa vigente con `/research`; no la inventes.

- Si prepagar deuda es la alternativa, la tasa es la de esa deuda — suele ganarle a cualquier idea.
- **No castigues el riesgo dos veces.** El fracaso ya está modelado con `p_exito` y el camino de fallo; súmale a la tasa solo una prima moderada por iliquidez (+3 a +6 pp), no la prima de "startup" de 30–50 % que usan los inversionistas que no modelan el fallo.

## `p_exito` — anclas de clase de referencia

Punto de partida, luego ajusta con evidencia de la candidata. Etiqueta siempre como `juicio` salvo que tengas datos propios.

| Situación de la candidata | `p_exito` inicial |
|---|---|
| Idea sin ninguna señal de demanda | 0.20 – 0.35 |
| Interés declarado (encuestas, likes, "lo compraría") | 0.30 – 0.45 |
| Preventas pagadas, lista de espera con abono, piloto con clientes que pagan | 0.50 – 0.70 |
| Modelo probado replicado (servicio conocido, franquicia, cliente ancla firmado) | 0.70 – 0.85 |

`p_exito` mide superar el criterio de muerte en `mes_corte`, no "que el negocio sea un éxito". Si la evidencia ya justifica un `p_exito` bajo, no además estires el rango pesimista de volumen por la misma razón.

## Qué métrica manda

| Métrica | Úsala para | Engaña cuando |
|---|---|---|
| Valor esperado | Ordenar por defecto | La distribución es muy sesgada: mira también P10 y P(VAN<0) |
| Valor esperado por peso expuesto | Capital es la restricción que ata | Candidatas pequeñas con valor absoluto irrelevante |
| P(mejor) | Comunicar la decisión a no financieros | Las candidatas están correlacionadas (mismo mercado) |
| VAN base | Explicar el caso central | Se reporta solo: es la moda, no la media |
| TIR | Comparar contra la tasa de una deuda | Candidatas excluyentes de distinto tamaño (favorece lo pequeño) o `tir_ambigua` |
| Payback | Restricción de liquidez ("necesito recuperar en 12 meses") | Se usa para ordenar: ignora todo lo posterior |

Una candidata con valor esperado positivo y P(VAN<0) > 50 % es una **apuesta asimétrica**: solo es aceptable si la pérdida de caja si falla cabe en la tolerancia. Ese perfil pide veredicto **Validar primero**, no **Implementar**.

## Cartera no excluyente

Si varias candidatas pueden coexistir, la pregunta cambia a "qué combinación cabe": ordena por valor esperado por peso, suma exposiciones de caja P90 y horas hasta agotar capital y tiempo, y revisa canibalización entre las elegidas. El script evalúa candidatas por separado; la combinación la armas tú sobre sus salidas.

## Trampas

Además de las seis condiciones de homologación del paso 2:

- **Volumen de manual.** "El 1 % de un mercado de X" no es un supuesto: es un deseo. Sin un embudo de abajo hacia arriba, el volumen se etiqueta `juicio` aunque venga de un informe sectorial.
- **Capital de trabajo olvidado.** Inventario, plazos de pago B2B de 30–60 días, IVA de importación adelantado: todos consumen caja aunque no sean costo.
- **Canibalización.** Una candidata que le quita ventas al negocio actual o a otra candidata se modela neta de lo que canibaliza.
- **Rangos a la medida.** Mover `rangos` o `p_exito` después de ver el ranking para salvar a la favorita. Todo cambio posterior a la primera corrida se justifica con evidencia nueva en `supuestos.md`.
- **Tiempo del fundador gratis.** Una idea que solo es rentable con horas a costo cero es un empleo mal pagado, no un negocio. Compara el VAN con y sin `valor_hora_fundador`.

## Lente cualitativa

Complementa, no reemplaza, al ranking financiero. Fija los pesos **antes** de puntuar; puntúa 1–5:

| Criterio | Pregunta |
|---|---|
| Ajuste estratégico | ¿Construye sobre activos, clientes o saberes que ya tienes? |
| Reversibilidad | ¿Puerta de dos vías (se deshace barato) o de una vía? |
| Tiempo al primer peso | ¿Cuántos meses hasta el primer ingreso real? |
| Valor de aprendizaje | ¿Qué capacidades u opciones abre aunque falle? |

Si la lente cualitativa elige otra candidata que el ranking financiero, no promedies: muestra la contradicción y su precio ("elegir B por ajuste estratégico cuesta 2,1M de valor esperado frente a A").
