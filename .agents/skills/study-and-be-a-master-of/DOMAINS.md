# Arquetipos de dominio

Puntos de partida para el **encuadre** y la **prueba de contacto**. Son hipótesis: cada ruta se prueba en vivo y cada regla se confirma en la investigación antes de entrar a la skill nueva.

La pregunta que ordena todo: ¿cuál es la **representación textual** del artefacto? El agente razona sobre texto. Una skill maestra existe para convertir el artefacto (flujo, libro, modelo, pieza) en un texto que el agente pueda leer, revisar y comparar, y para devolver los cambios por la vía segura.

| Dominio | Rutas de acceso (de mejor a peor) | Representación textual | Fuente de reglas de calidad | Skills a componer |
|---|---|---|---|---|
| **Power Automate** (ejemplo resuelto: `powerautomate-dev`) | Azure CLI token → `api.flow.microsoft.com`; Dataverse `workflow`; export de solución | `definition.json` → mapa en orden runAfter | Guías de codificación de Microsoft, límites de la plataforma | `excel-assist`, `diagnosing-bugs` |
| **Excel** | Archivo local u OneDrive sincronizado (openpyxl); Graph workbook API (token `az`); MCP Microsoft 365 | Mapa de hojas, rangos, fórmulas, nombres, validaciones | Fórmulas volátiles, referencias rotas, datos duros, tablas vs rangos | `excel-assist`, `context-extractor` |
| **Power BI** | Formato de proyecto PBIP/TMDL (texto); Power BI REST (token `az`, recurso `https://analysis.windows.net/powerbi/api`); XMLA | Modelo TMDL: tablas, relaciones, medidas DAX | Best Practice Analyzer (Tabular Editor), guía de modelado estrella | `entity-diagram-analysis`, `domain-modeling` |
| **Diseño 3D** | CAD paramétrico por código (OpenSCAD, CadQuery, FreeCAD Python); STL/3MF/STEP | Script paramétrico con cotas como variables | Espesores mínimos, piezas cerradas (manifold), tolerancias de encaje | `interactive-3d-structure`, `reverse-engineering` |
| **Impresión 3D** | CLI del slicer (PrusaSlicer, OrcaSlicer); API de la impresora (OctoPrint, Moonraker/Klipper); G-code | Perfil del slicer + resumen del G-code (tiempos, material, temperaturas) | Voladizos, soportes, orientación, material vs temperatura | `interactive-3d-structure`, `quotation-for` |
| **Estructuras de madera** | Cálculo por script según norma; planilla de cubicación | Tabla de piezas (sección, largo, carga, vano) | Norma local (Chile: NCh 1198 y relacionadas), tablas de vanos, factores de seguridad | `interactive-3d-structure`, `quotation-for`, `finantial-analysis` |
| **Diseño de procesos** | BPMN XML; entrevistas; datos del sistema (logs, tiempos) | BPMN XML + glosario | Reglas de validez BPMN (sin callejones sin salida, gateways balanceados), métricas de ciclo | `bpmn-diagram`, `domain-modeling`, `grill-with-docs` |

## Cuándo va RAG

Cuando el conocimiento del dominio vive en documentos grandes o privados (manuales del fabricante, normas en PDF, especificaciones internas), digerirlos con `context-extractor` a `references/` dentro de la skill nueva y apuntar desde `SKILL.md` a la sección exacta. Si el dominio cabe en `RESEARCH.md`, no hace falta RAG.

## Cuándo va MCP

Si hay un conector MCP para el dominio, es la primera ruta que se prueba. Si pide autenticación y la sesión no puede hacerla, el usuario debe autorizarlo en la configuración de conectores. Mientras tanto se prueba la ruta siguiente de la tabla, sin detenerse. En `SKILL.md`, nombrar la herramienta MCP en las dos formas (`mcp__<servidor>__<herramienta>` en Claude Code, `<servidor>/<herramienta>` en Antigravity; ver [RESEARCH.md §5.1](RESEARCH.md)), y dar siempre la ruta alternativa por si el servidor pide autenticación.

## Dominios físicos

Una skill sobre algo que carga peso, se calienta o se energiza separa lo que el agente **calcula** de lo que un **profesional firma**. La skill entrega el cálculo con la norma citada y marca como bloqueante la validación profesional cuando la norma la exige.
