# Research brief (plantilla)

Prompt para el agente de `/research`. Rellenar los `<...>` con lo que salió del **encuadre** y de la **prueba de contacto**. Pegar lo ya verificado en vivo para que el agente no lo re-investigue y se concentre en lo que falta.

```
Research task. Use ONLY primary sources (official vendor docs, REST/CLI references, specs,
the vendor's GitHub repos and SDK source). Cite the URL next to every claim. Label each claim
[OFFICIAL], [UNSUPPORTED-DOCUMENTED], [UNDOCUMENTED] (seen only in code/practice) or [INFERENCE].

Goal: feed a skill named "<nombre>" that lets an agent <verbos del encuadre: ver, evaluar,
construir, depurar...> <dominio> for a user who <contexto de uso>.

Already verified live (do not re-research, explain gaps instead):
- <ruta de acceso que funcionó, con endpoint/comando exacto y auth>
- <lo que devolvió vacío o dio error, y el código>

Answer in sections:
1. Access surfaces: every supported way to read/write <dominio> programmatically
   (API, CLI, SDK, MCP server, file format). For each: official or not, auth, what it can
   read vs write, endpoint shapes/versions, rate limits.
2. Object model: the schema/format of the artifact (definition, file structure, units),
   so a script can turn it into a readable map. Key fields for diagnosis.
3. Diagnostics: where errors, history and state live; status/error codes; documented
   causes of the common failures (<síntomas que reportó el usuario>).
4. Quality rules: official limits, best practices and anti-patterns, each phrased as
   "anti-pattern → recommendation" so it can become a lint rule. Include the vendor's own
   checker/analyzer tools if any.
5. Export/import for offline analysis.

Output: ONE Markdown file at <ruta de la skill>/RESEARCH.md. Start with a TL;DR for the skill,
then the sections, then "Doc conflicts" (where official pages contradict each other) and
"Open questions". Write no other file. Report back the key findings in a short summary.
```

Ajustes por tipo de dominio:
- **Físico** (impresión 3D, madera, estructuras): en la sección 4 pedir normas y tablas de diseño con su código oficial (p. ej. NCh en Chile), tolerancias, márgenes de seguridad, y qué decisión exige a un profesional certificado.
- **Proceso** (BPMN, operación): en la sección 2 pedir la notación estándar y en la 4 las reglas de validez del modelo.
