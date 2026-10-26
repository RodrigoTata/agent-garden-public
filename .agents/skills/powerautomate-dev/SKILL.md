---
name: powerautomate-dev
description: Reads, evaluates, simplifies and debugs Power Automate cloud flows from their make.powerautomate.com link or flow ID. Use when the user shares a Power Automate flow URL, asks why a flow isn't running, failed, got turned off or loses records, or wants a flow reviewed, optimized or simplified.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Power Automate Dev

Un flujo bueno es el **flujo mínimo**: el menor número de acciones por ejecución que hace el trabajo y que **grita** cuando falla. Todo lo que se hace aquí sirve a eso: menos acciones = menos requests, menos tiempo, menos lugares donde perder datos en **silencio**.

Herramienta: [scripts/pa.py](scripts/pa.py) (ruta relativa a la carpeta de esta skill, no al directorio de la sesión). Es de solo lectura y se autentica con Azure CLI (`az login` una vez; si falla con 401/AADSTS, pedir al usuario que corra `az login`). La API que usa (`api.flow.microsoft.com`) es la única que entrega el detalle por acción, pero Microsoft la declara **no soportada**. Si responde con errores de forma o de versión, ver [RESEARCH.md §1](RESEARCH.md) para las rutas oficiales (Dataverse `workflow`/`flowrun` y Power Platform API).

```
python pa.py get  <url|env flow> --out <dir>   # definition.json + map.md (árbol en orden runAfter)
python pa.py lint <dir>/definition.json        # hallazgos agrupados por regla, ALTA→INFO
python pa.py runs <url|env flow> [--top N] [--status Failed]   # sin runs → historial de trigger
python pa.py run  <url|env flow> <runId>       # estado/error/outputs por acción
python pa.py list <env> [texto]                # flujos hermanos visibles para ti
```

Guardar `<dir>` en el scratchpad de la sesión, nunca dentro del repo del usuario.

## Paso 0 — Mapa (todas las ramas)

1. `get` con el link. Leer `map.md` completo, no solo el encabezado.
2. Anotar: estado, trigger, conexiones y **qué escribe** el flujo (listas, tablas, correos, aprobaciones; con sus IDs).
3. `list <env> <palabra del nombre>`: otro flujo con el mismo trigger (p. ej. el mismo formulario) es un **gemelo**. Mapearlo también, porque dos flujos sobre un evento duplican costo y confunden el debug.

Hecho cuando: puedes decir en una frase qué entra, qué sale y a dónde, y sabes si tiene gemelos.

Luego elegir la rama según lo que pidió el usuario: **Evaluar** (revisar, optimizar, simplificar) o **Debug** (no corre, falló, se apagó, faltan registros). Si la pregunta es solo "¿qué hace este flujo?", el mapa es la respuesta.

## Rama Evaluar — llevarlo al flujo mínimo

1. `lint`. Cada hallazgo **ALTA** se confirma leyendo `definition.json` (el lint es heurístico; descartar los falsos positivos diciendo por qué).
2. Contar **acciones por ejecución** del camino típico: triggers + acciones ejecutadas, loops multiplicados por sus iteraciones esperadas. Esa es la cifra que baja la propuesta y la unidad de costo de la licencia ([RESEARCH.md §4.1](RESEARCH.md)).
3. Proponer el flujo mínimo aplicando el catálogo de [RESEARCH.md §4.2](RESEARCH.md). Los recortes que más rinden, en orden:
   - Filtrar en la fuente (`$filter`/`$top`/`$select`) en vez de loops con Condition.
   - Loop sobre una consulta de 1 resultado → `first(...)` y `$top=1`, con guarda `length(...) = 0` → alerta.
   - Ramas then/else que difieren en un dato → calcular el dato con `if()` o una tabla de configuración, y dejar una rama.
   - Filter array / Select en vez de Apply to each; nunca loops anidados.
   - Scope Try + Scope Catch (runAfter Failed, TimedOut) que notifique: el flujo mínimo **grita**.
   - Datos duros (correos, IDs) → variables de entorno o lista de configuración.
4. Entregar la propuesta como pasos para el diseñador, con el nombre nuevo de cada acción y las expresiones exactas. Si el usuario quiere, entregar también el JSON de las acciones que cambian.

Hecho cuando: cada hallazgo ALTA está resuelto en la propuesta o descartado con razón, y reportas acciones/ejecución **antes → después**.

## Rama Debug — encontrar dónde se pierde

Empezar siempre por la **cuadratura**: contar eventos en la fuente (respuestas del Form, filas nuevas, correos) contra registros en el destino, en la misma ventana de fechas. La diferencia dice cuánto se pierde y desde cuándo, antes de mirar una sola ejecución. Graph (`az account get-access-token --resource https://graph.microsoft.com`) lee listas SharePoint y Excel; Forms usa `--resource https://forms.office.com` sobre `formapi/api/forms('{id}')/responses`.

Luego descender por el primer síntoma que calce:

| Síntoma | Qué correr | Qué buscar |
|---|---|---|
| Estado `Stopped`/`Suspended` | `get` (campos `flowSuspension*`) | Causas documentadas de apagado en [RESEARCH.md §2.4](RESEARCH.md): 14 días de fallas, 90 días sin disparos, throttling, DLP, licencia, conexión rota. Si `flowSuspensionReason` es None, lo apagó una persona: preguntar quién y por qué antes de proponer encenderlo. |
| `Started` pero 0 ejecuciones | `runs` (cae al historial de trigger) | Trigger conditions que nunca calzan, conexión del trigger caducada, webhook desregistrado (recrear el trigger). |
| Ejecuciones `Succeeded` pero falta el efecto | `run <id>` de una ejecución afectada | Acciones `Skipped` con `ActionBranchingConditionNotSatisfied` y loops con 0 iteraciones: la pérdida **silenciosa**. |
| Ejecuciones `Failed`/`TimedOut` | `runs --status Failed`, luego `run <id>` | Primera acción `Failed` en el orden: su `error` y `outputs`. Las `Skipped` que siguen son consecuencia, no causa. |

El historial dura ~28 días ([RESEARCH.md §1.9](RESEARCH.md)). Más atrás, solo queda la cuadratura contra los datos.

Hecho cuando: nombras la causa con evidencia (ID de ejecución y acción, o conteo de la cuadratura), dices cuántos registros se perdieron (con sus IDs si es posible) y das el arreglo. Si la causa es de diseño, pasa por la rama Evaluar.

## Límites de acción

Todo lo anterior es lectura. **Pedir confirmación explícita antes de** encender o apagar un flujo, reenviar (resubmit) o cancelar ejecuciones, o escribir en listas o tablas para recuperar registros perdidos. Encender un flujo con aprobaciones o correos llega a personas reales, y un resubmit repite todos sus efectos (Power Automate es at-least-once). Nunca editar la definición por API: los cambios se proponen y el usuario los aplica en el diseñador o en una solución.
