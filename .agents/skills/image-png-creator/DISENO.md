# Diseño de las piezas

El sistema de [plantilla.html](plantilla.html): lienzo claro `#f8fafc`, cabecera en banda de color con emblema y objeto, secciones con barra lateral del color primario e ícono, bloques en tintas suaves y advertencias en rojo. Es claro y sin selector de tema porque el entregable es un PNG estático. La fuente HTML no se entrega como documento.

## Formatos

| Formato | `--ancho` | `--alto` | `--escala` | Texto mínimo | Uso |
|---|---|---|---|---|---|
| Folleto vertical | 1000 | libre | 2 | 13 px | Imprimir, WhatsApp, adjuntar |
| Infografía larga | 800 | libre | 2 | 14 px | Lectura con scroll en el teléfono |
| Post cuadrado | 1080 | 1080 | 1 | 24 px | Feed de redes |
| Historia | 1080 | 1920 | 1 | 28 px | Historias y estados |
| Banner o vista previa de enlace | 1200 | 630 | 1 | 28 px | Encabezado, tarjeta de enlace |

El `--ancho` de `render.mjs` y la variable `--ancho` de la plantilla llevan el mismo número. En formatos de alto fijo el contenido debe caber: si `render.mjs` avisa que se corta, recorta texto o pasa a un formato de alto libre. No achiques la letra bajo el mínimo. En post e historia, sube cada tamaño de la plantilla en proporción y deja como máximo tres bloques.

## Paletas por dominio

| Dominio | `--p` | `--p-osc` | `--p-luz` | `--p-fondo` |
|---|---|---|---|---|
| Salud, agro, naturaleza (por defecto) | `#059669` | `#047857` | `#10b981` | `#ecfdf5` |
| Técnico, procesos | `#1e6ba8` | `#174f7d` | `#3b8fd4` | `#eff6ff` |
| Operaciones, logística | `#b45309` | `#92400e` | `#f59e0b` | `#fffbeb` |
| Creativo, comunidad | `#6d3b8c` | `#542c6c` | `#9b5fc0` | `#f5f3ff` |
| Legal, finanzas | `#1e3a5f` | `#132741` | `#2f5d8f` | `#eef2f7` |

Las tintas de bloque (`.t1`–`.t4`, `.info`, `.aviso`) no cambian con el dominio: así un aviso rojo se lee como aviso en cualquier pieza.

## Bloques

| Bloque | Cuándo |
|---|---|
| `.cabecera` | Siempre. Título en mayúsculas de 2 a 5 palabras, bajada con el dato que define la pieza, etiqueta con el estado o alcance (piloto, interno, versión). |
| `.chips` | De 2 a 6 ítems cortos y paralelos: indicaciones, públicos, categorías. |
| `.grid3` + `.card` | Tres opciones o niveles comparables: cantidades, planes, tamaños. El `.punto` crece con el nivel. |
| `.barra` | Una sola regla que todos deben leer: frecuencia, horario, requisito. Como máximo una por sección. |
| `.card.paso` | Instrucciones en orden: de 3 a 4 pasos. Con más pasos, la pieza es un documento ([generate-html-doc](../generate-html-doc/SKILL.md)). |
| `.info` | Cuatro temas de consulta en dos columnas: conservación, requisitos, horarios, contacto. |
| `.avisos` | Advertencias, prohibiciones y riesgos. Siempre al final, antes del pie. |
| `footer` | Emisor, unidad y alcance real de la pieza. Nunca un sello, norma o registro que la ficha no respalde. |

Una pieza tiene como máximo 6 secciones. Cada tarjeta lleva frases de hasta 25 palabras. Si el contenido no cabe, se divide en dos piezas; la letra no se achica.

## Íconos

Solo los `<symbol>` del sprite de la plantilla, con `<svg class="i"><use href="#i-nombre"/></svg>` (`class="i s"` para el tamaño chico). Un emoji depende de la fuente del sistema donde se renderiza: puede salir vacío o como un cuadro.

Disponibles: `lista`, `balanza`, `mano`, `reloj`, `calendario`, `casa`, `edificio`, `termometro`, `sol`, `gota`, `hoja`, `frasco`, `alerta`, `prohibido`, `exclama`, `ojo`, `escudo`, `check`, `persona`, `grafico`, `dinero`, `ubicacion`, `herramienta`, `camion`, `rayo`, `corazon`.

Si falta uno, agrégalo al sprite como trazo de 24 × 24 con el mismo estilo (línea de 2, sin relleno). Las banderas, logos y emblemas se dibujan en SVG o vienen del humano. El logo de una organización real solo va si el humano lo entrega y la pieza es suya.
