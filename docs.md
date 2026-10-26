# Guía de Arquitectura

## Arquitectura General

AgentGarden es un repositorio de habilidades (*skills*) modulares diseñado para agentes de IA. La estructura del repositorio sigue el estándar de la plataforma Antigravity, organizando cada habilidad en un directorio independiente dentro de `.agents/skills/`.

Cada directorio de habilidad contiene de forma obligatoria un archivo principal `SKILL.md` que combina metadatos YAML frontmatter con instrucciones paso a paso en formato Markdown.

## Patrones de Diseño

### 1. Skill Encapsulado
- **Definición**: Cada habilidad se encuentra en su propia carpeta en `.agents/skills/<skill-name>/`.
- **Contrato**: El archivo `SKILL.md` especifica obligatoriamente los campos `name` y `description` en el encabezado YAML.
- **Recursos Adicionales**: Las habilidades complejas pueden incluir carpetas especializadas como `scripts/` (utilitarios), `references/` (documentación complementaria) o `resources/` (plantillas).

### 2. Flujo de Ejecución por Pasos
- Las habilidades estructuran su proceso mediante pasos numerados claros, definiendo un **Criterio de finalización** (*Completion criterion*) para cada etapa.
- Se implementan barreras de protección (*Guardrails*) para prevenir acciones destructivas o cambios no autorizados.

### 3. Dualidad de Ejecución (Orquestación vs. Standalone)
- Las habilidades de evaluación compleja (`cotizador-departamentos`, `cotizador-casas`) admiten dos modalidades operacionales:
  - **Modo Orquestación**: Delegan la prospección en `/research` y la maquetación visual en `/generate-html-doc`.
  - **Modo Standalone**: Ejecutan consultas web directas, validaciones financieras y ensamblado HTML inline de forma 100% autónoma.

### 4. Integridad y Verificación Activa de Enlaces
- Protocolo de validación técnica en tiempo real mediante consultas HTTP (`200 OK`) previo a la consolidación de reportes, previniendo redirecciones canónicas a buscadores o pantallas de error 404.

### 5. Motor de Asesoría Secuencial e Interrogación Interactiva (Grill-Me Integrado)
- Implementado en habilidades de formulación estratégica (`business-implementation-plan`, `grill-with-docs`).
- **Protocolo de Interacción**: Formula una sola pregunta a la vez estructurada con dos alternativas explícitas (Opción recomendada con justificación técnica/financiera vs. Opción alternativa con sus implicancias y trade-offs), consolidando hitos acordados antes de avanzar de fase.

### 6. Modelado Financiero y Cascada de Costos (Landed Cost & Unit Economics)
- Estandarización de cálculos para costeo de importación, distribución y retail:
  - Cascada de costeo internacional: Valor FOB $\rightarrow$ Valor CIF $\rightarrow$ Derechos Aduaneros Ad-Valorem ($6\%$) $\rightarrow$ Landed Cost Unitario.
### 7. Manipulación Segura de Binarios y Control de Bloqueos (Win32 Shared Access & Safe-Write)
- Implementado en `excel-assist` (`scripts/safe_excel.py`).
- **Problema que resuelve**: Los agentes de IA suelen fallar con errores de permisos (`Errno 13` / `Error 32: The process cannot access the file because it is being used by another process`) cuando el usuario mantiene abierto un archivo en Microsoft Excel o cliente de sincronización OneDrive.
- **Implementación**:
  - **Shared-Read en Memoria**: Bypassea bloqueos exclusivos utilizando llamadas Win32 API (`CreateFileW`) con flags de compartición `FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE`, leyendo el binario a un buffer `io.BytesIO` sin forzar el cierre del aplicativo cliente.
  - **Detección Atómica de Escritura (`check_write_lock`)**: Verifica la disponibilidad del descriptor antes de persistir, conmutando a archivos temporales de transición (`_temp.xlsx`) si el archivo está en edición activa por el usuario.

### 8. Living-Report Pattern (Reporte Evolutivo Sincronizado)
- Documento Markdown persistente (`docs/diagnostico-y-mejora-<nombre>.md`) que actúa como fuente única de verdad en auditorías de datos.
- A diferencia de reportes estáticos, se actualiza en tiempo real en cada ciclo de toma de decisiones del usuario y tras cada mutación confirmada en disco, manteniendo trazabilidad completa de normalizaciones taxonómicas, conversiones de tipo y semáforos ejecutivos.

### 9. Orquestación de la Tríada de Prototipado Físico (`start-a-proyect`)
- **Definición**: Orquestador integral para ingeniería de hardware, carpintería, cerramientos bioclimáticos y dispositivos IoT.
- **Tríada de Entregables**:
  1. *Gemelo Digital 3D Interactivo* (`interactive-3d-structure`): Modelo espacial autónomo con referencias direccionales y cotas métricas.
  2. *Cubicación, Sourcing y BOM Veteado* (`quotation-for`): Análisis de merma, optimización de cortes comerciales (piezas de 3.2m / rollos) y comparación de 3 opciones locales (Chile: Mercado Libre, Sodimac, Easy).
  3. *Manual de Montaje e Instructivo de Campo* (`generate-html-doc` + `agile-prototype`): Protocolo procedural paso a paso, seguridad EPP, checklist de QA y versionado por Marks (MKI, MKII).

### 10. Módulo Profundo y Costura Paramétrica en Gemelos Digitales 3D (`interactive-3d-structure`)
- **Costura Declarativa (`STRUCTURE_SPEC`)**: La física, piezas, escuadrías de madera, mallas técnicas, herrajes y vanos residen en un objeto de configuración desacoplado del motor gráfico.
- **Motor Gráfico Autónomo (`Structure3DEngine`)**: Three.js autónomo vía CDN en HTML único (cero compiladores locales). Incluye gizmo de brújula corner cube sincronizado, rosa de los vientos en el suelo, cotas interactivas en los 3 ejes y escala humana (1.75m).

### 11. Motor Dual-Theme y Aislamiento Estricto de Impresión (`generate-html-doc` & `writing-great-skills`)
- **Estándar Visual**: Todo documento HTML interactivo se renderiza en pantalla por defecto en **Modo Noche (Dark Glassmorphic)** con paleta grafito `#070b14`, tarjetas translúcidas y acentos de alto contraste.
- **Alternador Persistente**: Botón `☀️ Modo Claro / 🌙 Modo Noche` sincronizado en `localStorage`.
- **Aislamiento para Impresión (`@media print`)**: Anula forzosamente los fondos oscuros a blanco puro (`#ffffff`) y tipografía a negro (`#000000`), ocultando barras de herramientas (`.no-print`) para evitar consumo innecesario de tinta en papel o PDF.

### 12. Cabecera Estándar de Suite Interconectada (`.top-bar`)
- **Contrato de Navegación**: Todo documento entregable de un proyecto incorpora una barra superior sticky con identidad gráfica (`.brand`) y botones de acción rápida (`.top-actions`) enlazando directamente al visor 3D, cotización y manual instructivo, garantizando navegación bidireccional inmediata.

### 13. Habilitación de Invocación Autónoma y Metadatos de Skills
- **Descubrimiento por Modelos**: Se estandariza la eliminación de la directiva `disable-model-invocation: true` en todas las habilidades activas de `.agents/skills/`. Esto permite que el motor de inferencia de Antigravity descubra e invoque las habilidades autónomamente durante la resolución de tareas.
- **Metadatos Frontmatter Canónicos**: Todo `SKILL.md` debe mantener definidos de forma estricta los campos `name` (identificador canónico sin espacios) y `description` (resumen imperativo y triggers de activación en lenguaje natural), preservando la compatibilidad universal del catálogo.

### 14. Motor de Cálculo Determinista para Decisiones Financieras (`finantial-analysis`)
- **Problema que resuelve**: Los agentes cometen errores aritméticos al calcular VAN, TIR o probabilidades "de cabeza", y comparan ideas bajo varas distintas.
- **Implementación**: El agente traduce el libro de supuestos a un `modelo.json` declarativo; `scripts/fin_model.py` (solo librería estándar, semilla fija) proyecta flujos mensuales y emite `resultados.json`, `flujos.csv` y `resumen.md`. Ningún número del informe se calcula fuera del script.
- **Camino de fallo y opción cero**: Cada candidata tiene una probabilidad de superar su criterio de muerte (`p_exito`) en `mes_corte`; si no lo supera, se liquida sin gastar la inversión posterior, lo que premia escalonar la apuesta por Marks. La opción cero (no invertir) compite siempre en el ranking y en P(mejor).
- **Flujo económico vs. caja**: El tiempo del fundador se costea en el VAN pero no en la exposición de caja, evitando confundir costo de oportunidad con necesidad de capital.

### 15. Skills Maestras por Herramienta (`study-and-be-a-master-of` → `powerautomate-dev`)
- **Problema que resuelve**: El agente opina sobre herramientas (Power Automate, Excel, Power BI, 3D) sin llegar al artefacto real ni a fuentes oficiales, y cada sesión re-descubre cómo autenticarse y leerlo.
- **Patrón**: Una skill maestra se construye sobre un **espécimen** real del usuario. Primero la **prueba de contacto** (MCP, CLI autenticada como `az`, archivo local); luego la investigación de fuentes primarias a `RESEARCH.md` en segundo plano; un script de solo lectura que convierte el artefacto en **representación textual** (`get`), aplica reglas con fuente (`lint`) y diagnostica; y un `SKILL.md` con Paso 0 Mapa y una rama por verbo, cada una con su criterio de término.
- **Instalación dual**: La carpeta real vive en `.agents/skills/<nombre>/` (Antigravity) y `scripts/install_skill.py` valida el frontmatter y crea el junction `~/.claude/skills/<nombre>` para que Claude Code la vea de inmediato.
- **Límites de acción**: Leer es libre; encender flujos, reenviar ejecuciones o escribir datos que lleguen a personas o máquinas exige confirmación explícita.

### 16. Repositorio Central y Compatibilidad Dual de Invocación (`writing-great-skills`)
- **Problema que resuelve**: La dispersión de habilidades entre múltiples proyectos y la incompatibilidad de descubrimiento entre distintos entornos de agentes (Google Antigravity vs Claude Code).
- **Implementación**:
  - **Ubicación Centralizada por Defecto**: Toda nueva habilidad se aloja en `<AgentGarden>\.agents\skills\<skill-name>\`, a menos que se solicite expresamente asignarla a un repositorio específico.
  - **Invocación Universal con `/`**: Se estandariza el encabezado YAML (`name` y `description` en tercera persona con disparadores claros, sin etiquetas XML) y se vincula mediante junctions en Windows (`~/.claude/skills/<nombre>` y `.claude/skills/`), garantizando indexación en tiempo real para cualquier agente de codificación.

### 17. Blindaje de Commits y Cero Rastro de Coautoría de IA (`prepare-for-commit`)
- **Problema que resuelve**: Inserción inadvertida de trailers automatizados (`Co-authored-by: Claude <noreply@anthropic.com>`, firmas de modelos como "hecho con Claude Opus 5.5", "Gemini 3.8 Flash", etc.) que contaminan la trazabilidad y autoría del repositorio.
- **Implementación**: Guardrail estricto en el empaquetado de commits que prohíbe de manera absoluta cualquier firma, mención de proveedores (Anthropic, Google, OpenAI, etc.), modelos o trailers `Co-authored-by:`, restringiendo el mensaje al formato estándar humano de Conventional Commits (`type(scope): summary`).

### 18. Desacoplamiento Arquitecto-Worker y Tickets para Inicio en Frío (`execute` & `to-tickets`)
- **Problema que resuelve**: La disparidad de costo y capacidad cognitiva entre modelos de razonamiento avanzado y modelos ejecutores rápidos. Cuando un modelo ejecutor económico intenta abordar tareas complejas de desarrollo sin diseño previo, sufre de alucinaciones arquitectónicas, deriva en decisiones de diseño no acordadas y contamina el contexto.
- **Implementación**:
  - **Modos de Ejecución (`plan`, `build`, `full`)**: `execute` permite la partición estricta de responsabilidades. El arquitecto opera en modo `plan` (pasos 1 y 4) resolviendo todas las decisiones estructurales; el trabajador opera en modo `build` (pasos 2, 3 y 4) ejecutando código y pruebas sobre tickets ya definidos.
  - **Tickets Preparados para el Trabajador (*Worker-Ready*)**: Los tickets incorporan tres secciones obligatorias:
    1. *Costuras bajo prueba (`seams under test`)*: Interfaces públicas estandarizadas donde `tdd` debe verificar el comportamiento, eliminando la negociación de costuras durante la codificación.
    2. *Decisiones (`Decisions`)*: Formas de datos, manejo de errores, nombres canónicos y módulos intervenidos predeterminados.
    3. *Fuera de alcance (`Out of scope`)*: Límites negativos explícitos sobre lo que el trabajador tiene prohibido modificar o crear.
  - **Prueba de Inicio en Frío (*Cold-Start Test*)**: Cada ticket se valida de modo que un agente que solo tiene acceso al ticket y al repositorio (sin historial conversacional previo) no enfrente ninguna disyuntiva de diseño.
  - **Gestión Autónoma de Ambigüedades en Build**: Si un trabajador en modo `build` detecta una decisión de diseño no cubierta o una alteración de interfaz pública, no intenta improvisar: marca el ticket con estado `needs-architect`, anexa la pregunta técnica pendiente y salta de inmediato al siguiente ticket desbloqueado.

### 19. Tablero Kanban Sincronizado y Renderizado Declarativo (`create-kanban`)
- **Problema que resuelve**: La fragmentación de la gestión de requerimientos y tareas. Los tableros SaaS externos (Jira, Trello, Planner) introducen fricción de sincronización para los agentes, mientras que los archivos Markdown estáticos son difíciles de auditar visualmente por los usuarios humanos.
- **Implementación**:
  - **Fuente Única de Verdad en Markdown (`BOARD.md`)**: El backlog reside enteramente en el repositorio como archivos Markdown legibles y editables por agentes, con metadatos de configuración (`<!-- kanban: ... -->`), buzones por área (`inbox/`) y plantillas estándar (`_TEMPLATE.md`).
  - **Renderizador Determinista a HTML (`render_board.py`)**: Script autónomo en Python (sin dependencias externas) que compila `BOARD.md` en un dashboard interactivo `BOARD.html` estilo Notion con vistas de Tablero/Tabla, conmutador de tema claro/oscuro, filtros por área/prioridad y soporte de impresión apaisada.
  - **Prueba de Guardia y Cero Deriva (`test_board_html.py`)**: Test automatizado que verifica en CI que `BOARD.html` esté estrictamente sincronizado con `BOARD.md`, impidiendo discrepancias entre el estado de las tareas y el entregable visual.
  - **Interconexión con la Guía de Usuario**: Integración bidireccional mediante enlaces de barra superior (`.top-actions`), vinculando el manual interactivo del repositorio con su tablero operativo.

### 20. Árbol de Diseño por Rondas y Preguntas en la Frontera (`grilling`)
- **Problema que resuelve**: Las entrevistas de estrés y refinamiento de planes suelen divagar, asumir implícitamente decisiones clave o formular preguntas cuyas dependencias lógicas aún no están resueltas, trasladando además la carga de investigar hechos del entorno al usuario.
- **Implementación**:
  - **Mapeo del Espacio de Diseño como Árbol**: Las decisiones se modelan como un grafo donde cada disyuntiva se bifurca en ramas dependientes.
  - **Procesamiento de la Frontera por Rondas**: En cada ciclo se calcula la frontera de decisiones activas (aquellas cuyos prerrequisitos están completamente acordados). El agente expone todas las preguntas de la frontera en una única ronda numerada, acompañando cada una de su respuesta recomendada con justificación técnica.
  - **Separación Estricta de Hechos y Decisiones**: La recopilación de hechos (inspección de archivos, herramientas, código) se resuelve de forma 100% autónoma por el agente mediante sub-agentes o herramientas nativas; las decisiones estratégicas o de arquitectura se reservan exclusivamente para el usuario.

### 21. Escaneo por Fotos con Trazabilidad de Medidas y Contraste por Cámara (`3d-scanner`)
- **Problema que resuelve**: Una foto entrega forma y proporciones, pero no escala ni profundidad. Estimar medidas a ojo, o mezclarlas con las dadas por el usuario sin distinguirlas, produce gemelos que parecen exactos sin serlo.
- **Implementación**:
  - **Fuente por medida**: Cada número del inventario lleva exactamente una fuente (`medido`, `foto ✓` confirmada por el usuario, `foto` con ±10 %, `catálogo`, `supuesto`), que se copia a la `nota` de la pieza y a los avisos del visor. Si un `medido` contradice una estimación `foto` en más de 15 %, se revisa la lectura de esa foto.
  - **Ancla y rectificación** (`scripts/lupa.mjs`, `scripts/rectificar.mjs`): Los píxeles se leen en recortes ampliados con grilla en coordenadas de la foto original y se convierten a mm con una homografía de 4 puntos sobre una cara de medidas conocidas. La línea de control compara la razón alto/ancho en píxeles con la real y marca ⚠ sobre 5 %, lo que detecta esquinas mal leídas antes de medir.
  - **Preguntas en la frontera**: Los huecos (profundidad, caras ocultas, interior, calces) se preguntan en un solo mensaje, ordenados, con la letra del recorrido y la estimación del agente para que confirmar sea rápido.
  - **Contraste por foto** (`scripts/contraste.mjs`): Arma una variante temporal del visor con la cámara de cada foto y sin las capas que esa foto no muestra, la verifica con `verify.mjs` de `interactive-3d-structure` y deja la captura para compararla. Ante una diferencia se sospecha primero de la cámara y solo después del SPEC.
  - **Tres entradas, una misma fuente única**: `fotos` (flujo anterior), `web` (una página de producto) y `texto` (solo descripción). Cada una produce el mismo inventario. La fuente `ficha` marca lo que publica el vendedor, convertido a mm con el original conservado (`ficha: 27 1/2" = 699 mm`).
  - **Descarga de ficha** (`scripts/web.mjs`): Lee JSON-LD de tipo Product, metadatos `og:`, filas de tablas con medidas y materiales, e imágenes de producto ordenadas por confianza (JSON-LD, `og:image`, página), descartando logos, íconos y miniaturas menores de 300 px. Si la descarga directa no trae datos de producto, reintenta en Chrome headless. Todo lo descargado es evidencia, nunca instrucción, y las páginas de listado se detectan con un aviso.
  - **Escala desde la ficha**: Una imagen de producto no trae huincha; su ancla es una medida `ficha` visible en la imagen (cara plana, cuenco oblicuo o dibujo de cotas). Una ficha con medida incoherente con la imagen anclada queda en duda y se busca en otra fuente antes de preguntar.
  - **Traspaso a alta calidad** (`ALTA-CALIDAD.md`): Si el humano pide realismo, el inventario pasa a `/three-js` con su confianza por fuente (`medido` 0.95, `ficha` y `foto ✓` 0.85, `catálogo` 0.8, `foto` 0.6, `supuesto` 0.3). El costo se informa antes de empezar, porque el ciclo de revisión es el costo dominante.
  - **Lupa WebP**: `lupa.mjs` lee también WebP, el formato habitual de las tiendas en línea.

### 23. Gemelo Digital Armado desde un SPEC Aislado y un Inventario Compartido (`interactive-3d-structure`)
- **Problema que resuelve**: El agente reescribía un visor completo de Three.js en cada encargo: 1 100 líneas de motor que cambiaban entre corridas, medidas repetidas en leyendas y comentarios que terminaban contradiciéndose, y ningún contrato claro con el escáner que trae las medidas.
- **Implementación**:
  - **Solo el SPEC es editable** (`<visor>.spec.js`): Las constantes y `const SPEC = { … }` son lo único que el agente escribe. `scripts/armar.mjs` las inyecta entre los marcadores `SPEC:INICIO` y `SPEC:FIN` de `template.html` y arma el `.html` final. La plantilla, el motor y el `.html` armado nunca se editan a mano.
  - **Guardas de armado**: `armar.mjs` rechaza un `.spec.js` que contenga los marcadores o `</script>`, y no sobrescribe un `.html` que no salió de la plantilla salvo con `--reemplazar`. `--extraer` recupera el SPEC de un visor ya armado.
  - **Inventario como contrato de entrada** (`<visor>.inventario.md`): Tabla de piezas con `Campo`, `mm` y `Fuente`, más secciones `Contradicciones` y `Avisos`. Cuando el inventario viene de `/3d-scanner` (`Origen: 3d-scanner`), la skill no entrega por sí misma: devuelve el control al paso de contraste del escáner.
  - **Fuente única en el SPEC**: Cada número visible sale de una constante, incluidos los textos de `nota`, `avisos` y `cotas`. Las cotas generales (`cotasGlobales`) se apagan cuando un elemento como un grifo sube la envolvente por encima de la ficha, y se escriben a mano con las medidas publicadas.
  - **Verificación en dos viewports**: `verify.mjs` abre el visor en escritorio (1280×800) y móvil (390×844) con Chrome o Edge headless y solo imprime VERDE sin errores de consola o de red, con todas las piezas construidas y sin scroll horizontal. Sin navegador disponible, el visor queda explícitamente no verificado.
  - **Piezas a medida** (`constructores`): Formas que los tipos no arman, como el lavamanos cerámico con agujero elíptico y cuenco de revolución, se resuelven en el propio SPEC sin tocar el motor.

### 24. Diseño Frontal con Identidad Propia y Revisión contra Defaults (`frontend-design`)
- **Problema que resuelve**: Las interfaces generadas caen en los mismos defaults para cualquier asunto: crema con serif terracota, tarjetas idénticas con sombra gris, eyebrows en mayúsculas sobre cada título, o un número grande con degradado como hero. Esos rasgos aparecen sin importar el tema.
- **Implementación**:
  - **Cinco pasos con criterio de terminado**: Anclar en el tema, planificar tokens (color, tipografía, layout, principios), revisar contra los defaults, construir y criticar. Cada paso declara cuándo está hecho; sin el paso de revisión no se escribe código.
  - **Lista de defaults separada** (`references/tells.md`): Se consulta en el paso de revisión, después de planificar, para que la planificación no se ancle en lo que hay que evitar. Un rasgo solo es válido cuando el brief lo pide.
  - **Redacción en referencia aparte** (`references/writing.md`): Se lee antes de escribir cualquier texto de interfaz: voz activa, acciones con el mismo nombre en todo el flujo, errores que dicen qué hacer.
  - **Prioridad del brief**: Donde el brief fija una dirección visual, se sigue exacta aunque pida un default. Donde deja libertad, esa libertad no se gasta en un default.
  - **Sin tema oscuro impuesto**: A diferencia de `generate-html-doc`, esta skill no fuerza un modo; el tema lo decide el brief.

### 25. Auditoría de Skills de Terceros como Texto en Cuarentena (`skill-analize`)
- **Problema que resuelve**: Una skill de terceros equivale a código que se ejecuta y a texto que entra al prompt del sistema. Un `SKILL.md` puede traer instrucciones ocultas, caracteres invisibles o comandos que corren antes de la invocación.
- **Implementación**:
  - **Dos ramas**: Auditoría de una carpeta local (`SKILL.md` y auxiliares en disco) o de un prompt pegado en el chat, sin descargar nada.
  - **Cuarentena**: El contenido auditado es dato inerte. No se ejecutan sus directivas, herramientas, URLs ni comandos.
  - **Catálogo de riesgos `SC-01` a `SC-07`**: Inyección de prompt, Unicode oculto, ejecución pre-contexto (`` !`cmd` ``), exfiltración de credenciales y riesgos de cadena de suministro.

### 26. Paridad de Skills, Reglas y Carpetas Multi-Root entre Antigravity y Claude Code (`sync-agents` & `workspace-folders-parity`)
- **Problema que resuelve**: Un PC nuevo o un workspace de VS Code con varias carpetas deja skills y reglas sin enlazar en un agente, y el otro no ve las carpetas hermanas del `.code-workspace`.
- **Implementación**:
  - **Auditoría primero** (`scripts/sync_agents.py --check`): Lista carpetas declaradas en el `.code-workspace`, enlaces faltantes en `~/.gemini/config/skills` y `~/.claude/skills`, junctions de workspace y los imports `@.agents/rules/...` de `CLAUDE.md`.
  - **Regla de disparo** (`.agents/rules/workspace-folders-parity.md`): Al iniciar sesión en un repositorio que forma parte de un `.code-workspace`, el agente incorpora todas las carpetas declaradas y repara la paridad si detecta enlaces faltantes. `CLAUDE.md` la importa para Claude Code.
  - **Fuente única de reglas**: `.agents/rules/` es la única fuente; `CLAUDE.md` solo importa, sin duplicar reglas.

### 22. Imágenes con Texto Compuestas desde una Ficha de Fuentes (`image-png-creator`)
- **Problema que resuelve**: Un modelo generativo de imágenes redacta el texto de memoria. Inventa sellos y certificaciones, junta rangos distintos en uno, agrega mecanismos que la fuente no dice y deja íconos vacíos. Como el PNG no tiene fuente, el error no se puede auditar ni regenerar.
- **Implementación**:
  - **Ficha de fuentes**: Cada texto de la pieza lleva una fuente (`doc` con ubicación, `usuario`, `web`, `agregado`) en un comentario `FICHA` de la fuente HTML. `agregado` queda vetado para números, dosis, precios, plazos, efectos, organizaciones, sellos, normas y contactos. Ante dos fuentes en choque gana la más primaria y el choque se informa.
  - **Composición determinista** (`plantilla.html`, `DISENO.md`): Lienzo claro con cabecera en banda de color, secciones con barra lateral e ícono, bloques en tintas fijas y sprite de íconos SVG (sin emoji). Formatos con ancho, alto, escala y letra mínima, y paletas por dominio.
  - **Render con revisión** (`scripts/render.mjs`): Mide el contenido en una copia sonda calibrada al lienzo real, captura con Chrome o Edge sin ventana a la altura exacta y marca ⚠ ante texto desbordado, piezas fuera del lienzo, imágenes rotas o contenido que no cabe en el alto fijo. Lista las líneas con números para cotejarlas con la ficha.
  - **Rama Corregir**: Transcribe la imagen por zonas con `lupa.mjs` de `3d-scanner`, marca cada texto ✓, ✗ o ? contra su fuente, recompone la pieza y entrega la causa raíz con una tabla Antes / Problema / Ahora.

## Estructura de Directorios

- `.agents/skills/`: Directorio raíz de almacenamiento de todas las habilidades disponibles y activas en el repositorio.
- `.agents/skills/<skill-name>/SKILL.md`: Punto de entrada interpretado por el agente para ejecutar el flujo de trabajo.
- `.agents/skills/<skill-name>/references/`: Documentos de referencia técnica, guías normativas y fórmulas de soporte para la ejecución de la habilidad.
- `skills-to-review/`: Directorio de incubación y revisión preliminar para nuevas habilidades antes de su incorporación a `.agents/skills/`.

---

Licensed under the Apache License 2.0 — see [LICENSE](LICENSE).
