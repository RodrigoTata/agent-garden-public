---
name: study-and-be-a-master-of
description: Builds a new master skill that makes the agent an expert operator of one tool or craft (Power Automate, Excel, Power BI, 3D design, 3D printing, timber structures, process design…), grounded in live access to the user's real artifacts and in primary-source research. Use when the user wants the agent to master a tool, app or technical domain, or asks for a skill to analyze, build, evaluate or debug things in it.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Study and Be a Master Of

Una skill maestra convierte al agente en un operador experto de **una** herramienta u oficio. Sabe llegar al artefacto real, lo pasa a una **representación textual** que puede razonar, conoce las reglas del oficio con fuente y sabe cómo falla. Ejemplo resuelto: [powerautomate-dev](../powerautomate-dev/SKILL.md). Leerlo antes de empezar, porque es el estándar de llegada.

Todo gira en torno al **espécimen**: un artefacto real del usuario (un link de flujo, un libro, un modelo, una pieza) sobre el cual se prueba cada paso. Sin espécimen, la skill es suposición.

Destino por defecto: `<AgentGarden>\.agents\skills\<nombre>\`, salvo que el usuario diga que es para un repo específico. Nombre `<herramienta>-dev` para software (`powerbi-dev`) o `<oficio>-master` para oficios físicos (`timber-master`). Cuerpo en español y `description` en inglés, como el resto de AgentGarden.

## 1. Encuadre

Preguntar en texto plano, con alternativas y una recomendación (regla de AgentGarden: sin modales), hasta tener:

- **Herramienta exacta** y versión o plataforma (Power BI Service vs Desktop, Bambu vs Klipper).
- **Trabajos**: 2 a 4 verbos que el usuario hará con la skill (ver, evaluar, construir, depurar, cotizar…). Cada verbo será una rama de la skill.
- **Espécimen**: un artefacto real en su poder, con su ruta o link.
- **Límites**: qué no se toca y a quién llegan los efectos (correos, aprobaciones, máquinas, clientes).
- **Ideal de calidad** del oficio en una palabra (para Power Automate fue *flujo mínimo*). Será la palabra guía de la skill nueva.

Si el dominio es ambiguo o grande, pasar por `/grill-me-rg` antes de seguir.

Hecho cuando: los verbos están nombrados, el espécimen está en mano y el ideal de calidad está en una palabra.

## 2. Prueba de contacto

Llegar al espécimen con los propios medios del agente. Probar las rutas de [DOMAINS.md](DOMAINS.md) de mejor a peor:

1. Conectores MCP y CLIs ya autenticados (`az`, `gh`, `gcloud`…).
2. Archivos locales o sincronizados.
3. Exportación manual por el usuario.

Si un MCP pide autenticación que la sesión no puede hacer, avisarlo y probar la ruta siguiente.

Convertir el espécimen en su representación textual (mapa, árbol, tabla) y leerla completa. Anotar cada comando exacto que funcionó y cada ruta que falló, con su error. Ese registro va a la investigación.

Hecho cuando: el agente leyó el espécimen por sí mismo y puede decir en una frase qué contiene.

## 3. Investigar, en paralelo

Lanzar `/research` en segundo plano con [RESEARCH-BRIEF.md](RESEARCH-BRIEF.md), rellenado con lo del encuadre y la prueba de contacto. Destino: `RESEARCH.md` dentro de la carpeta de la skill nueva. Si el conocimiento del dominio vive en manuales o normas en PDF, digerirlos con `/context-extractor` a `references/` (ver [DOMAINS.md § Cuándo va RAG](DOMAINS.md)).

No esperar: el paso 4 avanza mientras tanto. No inventar hallazgos antes de que llegue el informe.

Hecho cuando: `RESEARCH.md` existe, cada afirmación tiene fuente, y las etiquetas oficial / no soportado / inferencia están puestas.

## 4. Instrumentar

Escribir `scripts/<herramienta>.py` en la skill nueva, con un subcomando por trabajo repetible:

- `get`: espécimen → representación textual en disco.
- `lint`: reglas de calidad, agrupadas por regla y ordenadas por severidad.
- Uno de diagnóstico por cada fuente de estado o historial.

El script resuelve rutas relativas a su propia carpeta (no al directorio de la sesión), responde a `--help`, nunca pregunta de forma interactiva y maneja sus errores con un mensaje que diga qué hacer (p. ej. "corre `az login`"). Va al script lo determinista (llamadas, parseo, conteos, reglas). Queda en `SKILL.md` el criterio (qué hallazgo importa, qué proponer). Todo el script es de **solo lectura**.

Correr cada subcomando sobre el espécimen e iterar hasta que la salida sea **señal**: hallazgos repetidos agrupados, nada de ruido (estados irrelevantes, avisos de dependencia), y cada hallazgo alto verificado a mano contra el espécimen. Al llegar `RESEARCH.md`, convertir sus anti-patrones en reglas del `lint`, citando la sección.

Hecho cuando: cada subcomando corrió sobre el espécimen, cada regla del `lint` tiene fuente en `RESEARCH.md` y no quedan falsos positivos sin explicar.

## 5. Escribir la skill

Invocar `/writing-great-skills` y escribir `SKILL.md` con esta forma:

- **Frontmatter**: solo `name` (igual a la carpeta) y `description`, según la lista de compatibilidad de [RESEARCH.md](RESEARCH.md) para Claude Code y Antigravity. La `description` va en inglés y en tercera persona, con la forma "Does X. Use when…": nombra la herramienta y los disparadores reales ("Use when the user shares a … link, asks why … fails…"), con 1024 caracteres como máximo y sin `<` ni `>`.
- **Palabra guía**: el ideal de calidad del encuadre, definido una vez arriba y usado en todas las ramas.
- **Paso 0 — Mapa**, común a todas las ramas: `get`, leer la representación completa y ubicar artefactos hermanos.
- **Una sección por verbo**: pasos, tabla síntoma → comando → qué buscar para depurar, y un criterio de **Hecho cuando** que se pueda verificar.
- **Referencias**: punteros a secciones exactas de `RESEARCH.md` (`§4.2`), nunca copias. Nombrar las skills de AgentGarden que componen cada rama (ver la columna de [DOMAINS.md](DOMAINS.md)).
- **Límites de acción**: lectura libre; toda escritura, encendido, envío o cambio que llegue a personas, máquinas o datos requiere confirmación explícita.

Hecho cuando: cada verbo del encuadre tiene su rama con criterio de término, y ninguna regla está duplicada entre `SKILL.md` y `RESEARCH.md`.

## 6. Probar en carne propia

Ejecutar la skill nueva desde cero sobre el espécimen, siguiendo `SKILL.md` al pie de la letra, como si fuera otro agente. Cada vez que haya que improvisar, la skill tiene un hueco: corregirla y repetir.

Probar también el disparo: escribir 3 frases reales del usuario que deberían invocarla y 2 cercanas que no, y verificar contra la `description` que distingue unas de otras.

Hecho cuando: una pasada completa sin improvisar produce al menos un hallazgo real y verificado sobre el espécimen, o un "limpio" con evidencia.

## 7. Instalar

```
python scripts/install_skill.py <nombre>
```

Valida el frontmatter y los enlaces, y crea el junction `~/.claude/skills/<nombre>` para que Claude la vea de inmediato con `/`. Si marca FALTA, agregar la fila en la tabla "Habilidades Disponibles" de `README.md` de AgentGarden y una nota en `docs.md`.

Hecho cuando: el script termina sin ERROR ni FALTA. Entregar al usuario el resumen: ramas, comandos, hallazgos sobre el espécimen y los límites de la skill (por ejemplo, APIs no soportadas).
