# AgentGarden

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Standard-Agent%20Skills-green.svg)](https://agentskills.io)

Colección modular de habilidades (*skills*) y recursos estandarizados de uso general para agentes de IA, compatible con el estándar abierto `.agents/skills/` (`agentskills.io`) en Google Antigravity, Claude Code, Cursor y cualquier entorno de asistencia agéntica.

## Características Clave

- **Estandarización de Skills**: Estructura homogénea basada en `SKILL.md` con metadatos en YAML frontmatter e instrucciones técnicas.
- **Flujos de Trabajo Especializados**: Habilidades enfocadas en arquitectura, revisión de código, TDD, depuración, formateo de repositorios, seguridad y documentación.
- **Portabilidad de Reglas**: Estructura compatible con el directorio `.agents/skills/` en la raíz de cualquier repositorio.

## Estructura del Proyecto

```
.agents/
├── rules/
└── skills/
    ├── 3d-scanner/
    ├── agile-prototype/
    ├── audit-me/
    ├── bpmn-diagram/
    ├── business-implementation-plan/
    ├── code-review/
    ├── codebase-design/
    ├── context-compactor/
    ├── context-extractor/
    ├── create-kanban/
    ├── cyber-audit/
    ├── debug/
    ├── devsecops-review/
    ├── diagnosing-bugs/
    ├── domain-modeling/
    ├── entity-diagram-analysis/
    ├── excel-assist/
    ├── execute/
    ├── finantial-analysis/
    ├── frontend-analysis/
    ├── frontend-design/
    ├── generate-html-doc/
    ├── grill-me-rg/
    ├── grill-with-docs/
    ├── grilling/
    ├── handoff/
    ├── image-png-creator/
    ├── implementation-plan/
    ├── improve-codebase-architecture/
    ├── interactive-3d-structure/
    ├── powerautomate-dev/
    ├── prepare-for-commit/
    ├── quotation-for/
    ├── repo-format/
    ├── research/
    ├── reverse-engineering/
    ├── rule-creating/
    ├── skill-analize/
    ├── start-a-project/
    ├── start-a-proyect/
    ├── study-and-be-a-master-of/
    ├── sync-agents/
    ├── tdd/
    ├── teach/
    ├── three-js/
    ├── to-qa/
    ├── to-spec/
    ├── to-tickets/
    ├── wayfinder/
    ├── web-audit/
    └── writing-great-skills/
skills-to-review/                                # Candidatas: pueden pasar al catálogo principal tras su revisión
├── ask-matt/
├── cotizador-casas/
├── cotizador-departamentos/
├── interior-exterior-designer/
├── show-me/
├── teach/
└── turn-into-rag/
docs/
└── architecture.md                               # Guía técnica de arquitectura
.github/
├── scripts/guard.mjs                             # Verificación de fugas (secretos, correos, rutas locales, licencias en SKILL.md)
└── workflows/guard.yml                           # Ejecuta la verificación en cada push y pull request
LICENSE                                           # Apache License 2.0
NOTICE                                            # Atribuciones de skills adaptadas de terceros
```

## Habilidades en Revisión (Skills to Review)

Estas skills viven en [`skills-to-review/`](skills-to-review/) y **aún no forman parte del catálogo principal**: podrían ser aceptadas en la lista principal tras su revisión.

| Skill | Descripción |
|---|---|
| **cotizador-departamentos** | Búsqueda, auditoría y cotización de departamentos residenciales con enlaces 100% verificados (HTTP 200), isócronas urbanas (10/20m pie, 5/15/30m auto, metro), amortización cuota a cuota en UF y CLP, Scorecard 0-10 y reporte HTML. |
| **cotizador-casas** | Valuación y cotización inmobiliaria residencial — análisis de entorno e isócronas (10/20m pie, 5/15/30m auto, metro), amortización hipotecaria cuota a cuota, Scorecard 0-10 y reporte HTML. |
| **ask-matt** | Entrevista y asesoría especializada basada en perfiles y criterios expertos. |
| **show-me** | Visualización rápida del contexto mediante diagramas concisos, árboles de llamadas, pseudocódigo, diffs y artefactos HTML focalizados. |

## Habilidades Disponibles (Skills)

| Skill | Descripción |
|---|---|
| **agile-prototype** | Planificación y ejecución ágil de iteraciones de prototipos (MKI, MKII) para hardware o software. |
| **audit-me** | Auditoría crítica implacable de propuestas, lógica de negocio, arquitecturas de dominio y código de software con stress-testing de invariantes y detección de fugas. |
| **bpmn-diagram** | Generación de diagramas de procesos de negocio BPMN 2.0 en HTML interactivo con bpmn-js (Camunda ref). |
| **business-implementation-plan** | Transformación de ideas de negocio en planes de implementación estructurados con costeo (Landed Cost), unit economics y hoja de ruta. |
| **code-review** | Revisión de código basada en estándares del repositorio y especificaciones del PR. |
| **codebase-design** | Vocabulario y patrones para el diseño de módulos profundos e interfaces limpias. |
| **context-compactor** | Compactación del historial de conversación en puntos de control minimalistas. |
| **context-extractor** | Extracción y digestión estructurada de documentos binarios (PDF, Excel, Word, PPT, CSV) a un almacén RAG local optimizado en tokens. |
| **create-kanban** | Andamiaje de tablero Kanban en Markdown (`BOARD.md`) con archivos por ítem, buzones por área y renderizado a HTML estilo Notion sincronizado mediante pruebas. |
| **cyber-audit** | Auditorías de seguridad y listas de verificación de vulnerabilidades. |
| **debug** | Triaje y diagnóstico de errores reportados en lenguaje natural. |
| **devsecops-review** | Verificaciones de seguridad DevSecOps y reporte en formato HTML + Markdown. |
| **diagnosing-bugs** | Ciclo sistemático de diagnóstico para fallas complejas y degradación de rendimiento. |
| **domain-modeling** | Definición del modelo de dominio, lenguaje ubicuo y decisiones de arquitectura (ADRs). |
| **entity-diagram-analysis** | Generación de diagramas Entidad-Relación en HTML interactivo separados por regiones para aislar el análisis y producir un resumen de arquitectura. |
| **excel-assist** | Auditoría, normalización, validación de datos, semáforos ejecutivos y modificación segura de libros Excel (.xlsx) con acceso compartido Win32 y living-reports. |
| **execute** | Ejecución autónoma de PRDs, specs o bugs de punta a punta (`full`) o particionada entre agente arquitecto (`plan`) y trabajador (`build`) mediante `to-tickets`, `tdd` y `to-qa`. |
| **finantial-analysis** | Comparación financiera de ideas, proyectos o prototipos para decidir cuál implementar: motor determinista (VAN, TIR, payback, exposición de caja, Monte Carlo con camino de fallo, tornado y valores de quiebre) contra la opción cero, con veredicto y criterio de muerte. |
| **frontend-analysis** | Análisis y mapeo de interfaces complejas (Cockpit / Digital Twin) generando guías visuales en HTML. |
| **frontend-design** | Diseño y construcción de páginas, interfaces y componentes con identidad visual propia del tema: plan de tokens, revisión contra los *tells* de diseño genérico, construcción y autocrítica. |
| **generate-html-doc** | Generación de documentos HTML estructurados e interactivos (instructivos, guías, manuales, reportes) con motor Dual-Theme (Modo Noche/Claro) y cabecera interconectada. |
| **grill-me-rg** | Entrevista interactiva para afinar planes y resolver decisiones de diseño. |
| **grill-with-docs** | Entrevista intensiva de diseño generando ADRs y glosario en el proceso. |
| **grilling** | Entrevista implacable al usuario para someter a estrés ideas, planes o decisiones mapeando un árbol de diseño por rondas en la frontera. |
| **handoff** | Compactación de la sesión en un documento de traspaso para continuidad entre agentes. |
| **3d-scanner** | Escaneo de objetos y espacios físicos hacia un gemelo digital 3D desde fotos, la página web de un producto (`scripts/web.mjs`: ficha JSON-LD, medidas del texto e imágenes) o solo una descripción en texto: lectura con visión (lupa con grilla y rectificación de perspectiva sobre una cara de medidas conocidas), pregunta al humano solo lo que la evidencia no entrega, trazabilidad de la fuente de cada medida (`medido`, `foto ✓`, `ficha`, `foto`, `catálogo`, `supuesto`) y contraste del modelo contra cada imagen. Construye con `interactive-3d-structure` y, para realismo, con `three-js`. |
| **image-png-creator** | Generación de imágenes PNG con texto (folletos, infografías, afiches, posts, banners) compuestas en HTML con una ficha de fuentes por texto (`doc`, `usuario`, `web`, `agregado`) y renderizadas con navegador sin ventana (`scripts/render.mjs`: altura exacta, desbordes, alto fijo y líneas con números para cotejar). Rama Corregir para imágenes con datos alucinados. |
| **implementation-plan** | Diseño de planes de implementación des-riesgados con costuras arquitectónicas, diseño de verificación y gate de aprobación de usuario. |
| **improve-codebase-architecture** | Evaluación y propuestas de mejora para la arquitectura del sistema. |
| **interactive-3d-structure** | Generación de gemelos digitales y estructuras 3D interactivas en Three.js con costura declarativa, cotas, brújula cardinal y escala humana. El agente escribe solo `<visor>.spec.js` y `scripts/armar.mjs` lo inyecta en la plantilla; recibe las medidas por `<visor>.inventario.md`, el contrato compartido con `3d-scanner`. |
| **look-for** | Búsqueda en portales de avisos y marketplaces (Facebook Marketplace, Mercado Libre, Chileautos, Yapo) con navegador sin ventana; devuelve una terna verificada y una recomendación. |
| **powerautomate-dev** | Lectura, evaluación, simplificación y depuración de flujos de Power Automate desde su link (Azure CLI): mapa en orden runAfter, lint de 10 reglas con fuente oficial, historial de ejecuciones y detalle por acción, cuadratura origen/destino. |
| **prepare-for-commit** | Sintetiza deltas en la documentación y prepara la propuesta de commit convencional. |
| **quotation-for** | Búsqueda y comparación de cotizaciones de productos/servicios en el mercado (por defecto Chile) con dashboard interactivo y plan de corte. |
| **rea** | Ingeniería inversa de binarios nativos, código administrado, paquetes Electron/ASAR, APKs y firmware mediante REA (servidor MCP o CLI), con evidencia verificada por hash. |
| **repo-format** | Formatea o estructura repositorios según estándares de ingeniería de software (scaffold/tidy). |
| **research** | Investigación técnica en segundo plano consultando fuentes primarias oficiales. |
| **reverse-engineering** | Análisis e ingeniería inversa sistemática de productos físicos o servicios de software para guiar nuevos desarrollos. |
| **rule-creating** | Creación, modificación y auditoría de reglas operacionales y guardrails permanentes para agentes en cualquier espacio de trabajo. |
| **skill-analize** | Guardia de seguridad y auditoría estática/semántica para skills de terceros (`SKILL.md`, scripts auxiliares o prompts pegados en el chat desde Hugging Face/GitHub): detecta prompt injection, Unicode smuggling, ejecución pre-contexto (`` !`cmd` ``), exfiltración de credenciales y riesgos de supply chain (`SC-01`..`SC-07`). |
| **start-a-project** | Alias de conveniencia para `start-a-proyect`. |
| **start-a-proyect** | Orquestador maestro para proyectos físicos (sombraderos, carpintería), IoT/3D print y digitales articulando la Tríada (3D, Cotización y Manual). |
| **study-and-be-a-master-of** | Fábrica de skills maestras para una herramienta u oficio (Excel, Power BI, 3D, madera, procesos…): encuadre, prueba de contacto sobre un espécimen real, investigación de fuentes primarias, script de solo lectura, redacción con `writing-great-skills`, prueba en carne propia e instalación agnóstica (Antigravity / Claude Code). |
| **sync-agents** | Sincronización automática de skills, reglas (`.agents/rules/` y `CLAUDE.md`) y visibilidad de carpetas multi-root (`.code-workspace`) entre Google Antigravity y Claude Code en cualquier PC. |
| **target-profiling** | Perfilado de personas de interés con metodología de inteligencia (OSINT, ciclo de inteligencia, análisis de vínculos) a partir de fuentes públicas. |
| **tdd** | Desarrollo guiado por pruebas (red-green-refactor) y estrategias de mocking/testing. |
| **teach** | Flujos educativos, rutas de aprendizaje, misiones y registros de avance. |
| **three-js** | Reconstrucción procedural de objetos y personajes 3D en Three.js a partir de imágenes de referencia: pipeline de escultura por fases, contratos de calidad, rig/animación y auto-corrección visual. |
| **to-qa** | Verificaciones de QA automatizado y planificación de pruebas manuales. |
| **to-spec** | Transformación de requerimientos o ideas en especificaciones técnicas detalladas (PRD/Spec). |
| **to-tickets** | Desglose de especificaciones en vertical slices trazadoras con costuras de prueba preacordadas (*seams under test*) y especificación de tickets preparados para ejecución en frío (*worker-ready*) con decisiones cerradas. |
| **wayfinder** | Mapeo y gestión de iniciativas complejas divididas en mapas de tickets de decisión. |
| **web-audit** | Auditoría y análisis completo de sitios web. |
| **writing-great-skills** | Guía de buenas prácticas y vocabulario para redactar skills predecibles, incorporando el patrón de UI Dual-Theme. |

---

## Licencia

Este proyecto está licenciado bajo la [Apache License 2.0](LICENSE). Copyright 2026 Rodrigo González.

## Créditos y atribuciones

Varias skills están adaptadas de proyectos de código abierto y mantienen la atribución de sus autores reales en el bloque `metadata` de su `SKILL.md` (`author`, `source`, `upstream-license`, `adapted-by`). Los avisos de copyright y licencias originales se reproducen en [NOTICE](NOTICE).

| Origen | Autor | Licencia | Skills |
|---|---|---|---|
| [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock | MIT | `code-review`, `codebase-design`, `diagnosing-bugs`, `domain-modeling`, `grill-with-docs`, `grilling`, `grill-me-rg`, `handoff`, `improve-codebase-architecture`, `research`, `tdd`, `teach`, `to-spec`, `to-tickets`, `wayfinder`, `ask-matt` (en revisión) |
| [img2threejs](https://github.com/img2threejs/img2threejs) | hoainho | Apache-2.0 | `three-js` |
| [morluto/rea](https://github.com/morluto/rea) | morluto | MIT | `rea` |

Las skills adaptadas de proyectos MIT conservan la licencia MIT (`license: MIT` en su frontmatter); el resto del repositorio es Apache-2.0.

Todas las skills están formateadas con `writing-great-skills` para funcionar con Gemini (Google Antigravity) y Claude Code.
