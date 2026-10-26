---
name: finantial-analysis
description: Compara financieramente ideas, proyectos o prototipos para decidir cuál implementar. Usar cuando el usuario quiera elegir entre varias ideas o proyectos, saber si una sola idea vale la pena, pida un análisis financiero (VAN, TIR, payback, flujo de caja), o cuando otra skill necesite un veredicto financiero go/no-go.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Finantial Analysis — ¿cuál idea implementar?

Llega una **cartera**: dos o más ideas, proyectos o prototipos compitiendo por el mismo capital y tiempo, o una sola idea que debe ganarle a no hacer nada. Esta skill las homologa, las modela en código y entrega un veredicto por candidata.

## Palabras guía

- **Opción cero**: no invertir; el capital queda rindiendo su costo de oportunidad. Compite siempre, con VAN 0 por definición. Si ninguna candidata le gana, gana ella.
- **Homologar**: poner todas las candidatas bajo la misma vara antes de compararlas (condiciones en el paso 2).
- **Supuesto crítico**: el driver que más mueve el VAN (primera barra del tornado). La decisión se juega ahí.
- **Valor de quiebre**: el valor del supuesto crítico con el que el VAN llega a 0, en unidades reales.
- **Criterio de muerte**: umbral numérico con fecha que, si no se alcanza, detiene la candidata. Se deriva del valor de quiebre.

## Reglas

- **Ningún VAN, TIR, payback, escenario ni probabilidad se calcula a mano.** Todo número del informe sale de `scripts/fin_model.py`.
- Las preguntas al usuario siguen `/grill-me-rg`: una por mensaje, en texto plano, dos alternativas con recomendación. Pregunta solo lo que los artefactos existentes no respondan.
- Trabaja en `docs/analisis-financiero/<slug>/` del proyecto activo. `supuestos.md` es la fuente única de cartera, envolvente y supuestos.

## 1. Encuadrar la cartera

Antes de preguntar, lee lo que ya exista de cada candidata: `docs/vision.md` y `version_log.md` de `/agile-prototype`, planes de `/business-implementation-plan`, cotizaciones de `/quotation-for`, specs o código del repo. Documentos binarios (PDF, Excel, Word) → `/context-extractor`.

Registra por candidata: tesis en una línea, tipo (producto físico, software, servicio, ahorro interno), etapa (idea, prototipo, en operación) y si excluye a las demás.

- **Más de 4 candidatas**: tamiza antes de modelar. Descarta las que fallen una pregunta eliminatoria (¿cabe en el capital?, ¿hay un bloqueo legal o técnico?, ¿existe alguna señal de que alguien pagaría?) hasta dejar 4 o menos, con el motivo de cada descarte.
- **Una sola candidata**: compite contra la opción cero y contra sus variantes si existen (MKI-a vs MKI-b, canal A vs B, comprar vs arrendar).

Fija la **envolvente de decisión**: capital disponible, pérdida máxima tolerable, horas/mes disponibles, horizonte (default 36 meses), tasa de descuento y criterio de ranking. Para elegir tasa y criterio, lee [references/criterios-y-trampas.md](references/criterios-y-trampas.md).

**Criterio de completitud**: `supuestos.md` lista cada candidata con sus cuatro atributos más la opción cero, y los seis campos de la envolvente tienen valor, declarado por el usuario o default aceptado explícitamente.

## 2. Levantar supuestos

Para cada candidata, cada driver (volumen, precio, costo variable, costos fijos, inversión, crecimiento, churn si es recurrente, `p_exito`, `mes_corte`) necesita base, rango pesimista–optimista y etiqueta de evidencia: `dato` (venta real, factura, cotización), `benchmark` (fuente externa citada) o `juicio`.

- Capex, BOM e insumos → `/quotation-for`. Precios de competencia, tasas de conversión, churn de referencia → `/research`.
- Importación o retail → landed cost y márgenes por canal con `references/unit-economics-guide.md` de `/business-implementation-plan`.
- Prototipos → inversión escalonada por Marks de `/agile-prototype`: MKI en el mes 0, MKII después de `mes_corte`.
- Volumen, siempre de abajo hacia arriba: tráfico × conversión, capacidad × ocupación.

**Homologa** todas las candidatas:

1. Mismo horizonte, moneda y tasa de descuento.
2. Precios y costos netos, sin IVA.
3. Solo flujos incrementales desde hoy: lo ya gastado es costo hundido.
4. Horas del fundador declaradas y costeadas.
5. Mismo régimen tributario.
6. Mismo nivel de detalle: una idea vaga no compite contra un plan maduro.

Antes de cerrar el paso, recorre la sección *Trampas* de [references/criterios-y-trampas.md](references/criterios-y-trampas.md) contra cada candidata.

**Criterio de completitud**: el libro de supuestos no tiene celdas vacías, todo `dato` y `benchmark` cita su fuente, y las seis condiciones de homologación se cumplen en cada candidata.

## 3. Modelar

Copia [scripts/ejemplo_modelo.json](scripts/ejemplo_modelo.json) a `modelo.json` y tradúcelo desde el libro de supuestos. Esquema, formas de modelar cada tipo de idea y significado de cada salida: [references/modelo.md](references/modelo.md).

```bash
python <AgentGarden>/.agents/skills/finantial-analysis/scripts/fin_model.py modelo.json --out resultados.json --csv flujos.csv --md resumen.md
```

Cada alerta se corrige en el modelo o se acepta con justificación en `supuestos.md`.

**Criterio de completitud**: el script termina sin error, existen `resultados.json`, `flujos.csv` y `resumen.md`, y ninguna alerta quedó sin corregir ni aceptar.

## 4. Estresar

Somete a `/audit-me` (modo *Ideas, Estrategia y Planes*) las dos primeras del ranking junto con su libro de supuestos. Suma un pre-mortem por candidata: "pasaron 18 meses y fracasó; ¿por qué?". Cada hallazgo:

- **cuantificable** → entra al modelo y el paso 3 se vuelve a correr;
- **no cuantificable** → matriz de riesgos en `supuestos.md`, con mitigación.

Una candidata que falla un filtro pero admite re-escalarse (lote más chico, menos horas) entra al modelo como candidata nueva re-escalada.

**Criterio de completitud**: cada hallazgo está en el modelo re-corrido o en la matriz de riesgos, y el ranking que usará el paso 5 es el de la última corrida.

## 5. Dictar veredicto

Cada candidata recibe exactamente uno. Evalúa las filas en orden; la primera que se cumple manda:

| Veredicto | Cuándo |
|---|---|
| **Descartar** | Falla un filtro que no admite re-escalarse, fue reemplazada por su versión re-escalada, o su valor esperado ≤ 0 y su valor de quiebre exige un cambio que la evidencia no sostiene. |
| **Implementar** | Valor esperado > 0, pasa los filtros, P(VAN<0) ≤ 50 % y su supuesto crítico descansa en `dato`. |
| **Validar primero** | Todas las demás: la decisión depende de un supuesto que un experimento barato puede resolver. |

Si ninguna candidata supera a la opción cero, dilo sin rodeos: el veredicto es no invertir todavía. Si las candidatas no se excluyen, el veredicto recae sobre la combinación: sigue *Cartera no excluyente* de [references/criterios-y-trampas.md](references/criterios-y-trampas.md).

Para **Validar primero**, diseña el experimento: su pregunta central es el supuesto crítico, su costo no supera la pérdida de caja si falla, y su criterio de muerte es el valor de quiebre en unidades y fecha ("≥ 5,4 ventas/mes promedio al día 90; bajo eso, se detiene").

Aplica la *Lente cualitativa* de [references/criterios-y-trampas.md](references/criterios-y-trampas.md) por separado. Si contradice el ranking, muestra la contradicción y su precio en valor esperado; no promedies.

**Criterio de completitud**: cada candidata tiene un solo veredicto, y el de la ganadora nombra su supuesto crítico, su valor de quiebre en unidades reales y un criterio de muerte con número y fecha.

## 6. Entregar

Genera `informe.html` con `/generate-html-doc`, en este orden: veredicto (la conclusión, la cifra que la sostiene y la cifra que la cambiaría), cartera y envolvente, tabla comparativa, supuestos críticos y valores de quiebre, tornado y distribución de valor, riesgos, próximos pasos.

Deriva el siguiente paso de la ganadora:

- **Validar primero** → `/agile-prototype`, con el experimento como MKI y el criterio de muerte como señal de éxito.
- **Implementar** → `/business-implementation-plan` si es un negocio comercial, `/start-a-proyect` si es un proyecto físico o IoT, `/to-spec` si es software.
- **Opción cero** → registra qué evidencia reabriría la decisión.

Cuando un experimento entregue datos reales, vuelve al paso 2: esos supuestos pasan a `dato` y el veredicto se recalcula.

**Criterio de completitud**: `informe.html` existe, su primera pantalla muestra veredicto, valor esperado y la cifra que cambiaría la decisión, y cada número del informe coincide con `resultados.json`.
