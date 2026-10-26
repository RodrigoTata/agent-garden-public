---
name: cotizador-departamentos
description: Busca, audita y cotiza departamentos residenciales para compra o inversión con enlaces 100% verificados — analiza entorno urbano con isócronas (10/20m pie, 5/15/30m auto, metro), modela amortización cuota a cuota en UF y CLP, evalúa con scorecard (0-10) y genera reporte interactivo en HTML. Use when the user asks to cotizar departamentos, buscar o comparar departamentos en venta, evaluar avisos de portales inmobiliarios, analizar conectividad a metro y terrazas, o simular hipotecas de propiedades en altura.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# cotizador-departamentos

**Audita** y cotiza departamentos residenciales a partir de criterios de búsqueda (comunas, presupuesto en UF, dormitorios, baños, piso/altura, terraza) o enlaces directos de portales (Portal Inmobiliario, TOCTOC, Mercado Libre), asegurando **verificación técnica estricta de enlaces activos**, contrastando métricas contra el mercado real, analizando el entorno mediante **isócronas de desplazamiento**, modelando la estructura crediticia con **amortización cuota a cuota**, aplicando un **scorecard multicriterio (0 a 10)** y generando un **informe de evaluación interactivo en HTML** con hoja de ruta de visitas y ofertas.

Las palabras guía son **auditar**, **verificar**, **isócronas**, **scorecard** y **scaffold**: cada ejecución sigue un proceso riguroso y determinista que garantiza publicaciones reales sin enlaces rotos, evalúa la calidad de vida en altura y entrega una recomendación financiera fundamentada.

---

## Modos de Ejecución

Este skill puede orquestar sub-skills o ejecutarse de forma **100% autónoma (standalone)**:

- **Con sub-skills activas:** 
  - Delega la investigación de fuentes primarias y benchmarking en `/research`.
  - Delega la maquetación y diseño visual imprimible en `/generate-html-doc`.
- **Modo Standalone (sin otras skills):** 
  - Realiza directamente las consultas web contra el índice activo de portales, verifica los códigos de respuesta HTTP de cada URL, calcula las proyecciones financieras y construye el archivo HTML autocontenido con el sistema de diseño embebido.

---

## Proceso de Evaluación y Cotización

```
Entrada (Requerimientos de Búsqueda o Enlaces)
   │
   ▼
[Paso 1: Búsqueda y Selección de Propiedades Candidatas]
   │
   ▼
[Paso 2: Validación Técnica de Enlaces y Fichas Activas] ◄─── (Verificación HTTP 200 / Ficha Única)
   │
   ▼
[Paso 3: Benchmarking de Mercado, Ratio UF/m² y Rentabilidad] ◄ (/research o búsqueda directa)
   │
   ▼
[Paso 4: Análisis de Entorno Urbano, Isócronas & Metro] ◄─── (10/20m pie, 5/15/30m auto)
   │
   ▼
[Paso 5: Estructura Financiera & Amortización Cuota a Cuota] ◄ (UF y CLP, Tasa Nominal y CAE)
   │
   ▼
[Paso 6: Scorecard Multicriterio (0-10) y Estrategia de Oferta] (5 dimensiones ponderadas)
   │
   ▼
[Paso 7: Generación del Reporte HTML Autocontenido] ◄──────── (/generate-html-doc o inline)
```

---

### Paso 1 — Búsqueda y Selección de Propiedades Candidatas

Recopilar los requerimientos del usuario o extraer los parámetros clave de las unidades:

1. **Filtros Clave de Búsqueda:**
   * **Tipología:** Dormitorios (ej. 2D mariposa o tradicionales) y baños (2B o suite + visita).
   * **Superficie y Espacios Exteriores:** m² útiles, m² totales y metraje de terraza privada (ej. 5 a 10 m² o azotea privada).
   * **Emplazamiento y Altura:** Piso mínimo (ej. piso 8 o superior, priorizando últimos pisos / penthouses sin vecinos arriba ni bloqueos visuales).
   * **Rango de Precio:** Presupuesto objetivo en UF (ej. 5.000 UF ± 500 UF) y valor en moneda local.
   * **Ubicación Geográfica:** Comunas y microzonas residenciales prioritarias (ej. Las Condes, Ñuñoa, Providencia).
   * **Equipamiento Inmueble:** Estacionamientos subterráneos y bodegas (con verificación de roles de contribuciones independientes).

**Criterio de completitud:** Conjunto de unidades candidatas identificadas (típicamente 3 a 5 opciones comparativas) que cumplan con todos los filtros duros.

---

### Paso 2 — Validación Técnica de Enlaces y Fichas Activas (Regla Crítica)

> [!IMPORTANT]
> **REGLA DE INTEGRIDAD DE ENLACES:** Nunca inventar, deducir o estructurar URLs hipotéticas. Las publicaciones inmobiliarias rotan con frecuencia y los portales redirigen rutas genéricas a buscadores o páginas de error 404.

Para cada propiedad seleccionada:

1. **Verificación de Respuesta HTTP en Vivo:**
   * Consultar la URL mediante herramienta de lectura de contenido (`read_url_content`) para confirmar que el servidor responde con **código HTTP 200** y contiene el título real de la publicación, fotos y precio.
2. **Extracción del Identificador Canónico:**
   * Extraer la URL canónica directa de la propiedad (ej. `https://www.portalinmobiliario.com/MLC-[ID-NUMERICO]-[SLUG]_JM` o ficha individual de TOCTOC).
3. **Control de No-Duplicación:**
   * Asegurar que cada opción del reporte tenga su **URL única e independiente**. Queda estrictamente prohibido reutilizar la URL de una opción en las demás filas o tarjetas.
4. **Verificación de Tipo de Vista:**
   * El enlace debe abrir la **ficha de detalle individual del departamento** (con galería de fotos, descripción y contacto del corredor), **NO** un listado de resultados de búsqueda con filtros.

**Criterio de completitud:** 100% de los enlaces probados y confirmados como publicaciones activas y directas antes de redactar el informe.

---

### Paso 3 — Benchmarking de Mercado, Ratio UF/m² y Rentabilidad

Analizar la competitividad económica de cada departamento frente a su entorno:

1. **Métricas de Valor por Superficie:**
   * Ratio base **UF/m² útil** y **UF/m² total**.
   * Comparación contra el promedio comunal de la tipología y la media de la microzona.
   * Cálculo de porcentaje de sobreprecio o descuento frente al mercado.
2. **Costos Operacionales Fijos:**
   * Gasto común mensual ordinario ($/mes) y si incluye agua caliente o calefacción central.
   * Contribuciones trimestrales (desglosando rol del departamento, rol de bodega y rol de estacionamiento).
3. **Cap Rate y Proyección de Renta:**
   * Canon mensual de arriendo estimado para la tipología y sector.
   * **Cap Rate Bruto Anual:** $\frac{\text{Arriendo Mensual} \times 12}{\text{Precio Total en UF}} \times 100$.
   * **Cap Rate Neto (NOI):** Descontando 4 cuotas de contribuciones y 1 mes de vacancia/mantención anual.

**Criterio de completitud:** Ratios UF/m² y Cap Rates calculados y documentados para todas las opciones evaluadas.

---

### Paso 4 — Análisis de Entorno Urbano, Isócronas y Conectividad

Estructurar la auditoría territorial de cada unidad en **anillos concéntricos de tiempo de desplazamiento (isócronas)**:

#### 1. Anillos a Pie (Walking Rings)
* **10 minutos a pie (~800 m — Radio de proximidad diaria):**
  * Supermercados exprés, minimarkets, panaderías, farmacias, cafeterías de barrio y servicios.
  * Paraderos de transporte público troncal (buses Red).
  * Plazas y áreas verdes de escala vecinal.
* **20 minutos a pie (~1,6 km — Radio vecinal consolidado):**
  * Estaciones de Metro más cercanas (líneas, nombre de estación y tiempo exacto a pie).
  * Supermercados de gran formato (Jumbo, Líder, Unimarc) y strip centers.
  * Colegios, centros de salud ambulatoria y polos gastronómicos/culturales.

#### 2. Anillos en Vehículo (Driving Rings)
* **5 minutos en auto (~2–3 km):**
  * Conexión a autopistas urbanas y vías estructurantes (ej. Costanera Norte, Vespucio/AVO, Kennedy).
  * Centros de salud zonales y clubes deportivos.
* **15 minutos en auto (~8–10 km — Polos de Empleo y Salud Compleja):**
  * Centros financieros y de negocios (El Golf, Nueva Las Condes, Providencia, Santiago Centro).
  * Malls regionales (Costanera Center, Parque Arauco, Alto Las Condes, Mall Plaza Egaña).
  * Clínicas de alta complejidad y campus universitarios.
* **30 minutos en auto (Conectividad Interurbana / Aeropuerto):**
  * Aeropuerto Internacional y accesos interregionales en horario valle.

#### 3. Matriz de Conectividad en Metro
* Tabla comparativa con los tiempos de viaje en la red de Metro desde cada propiedad hacia los principales nodos de la ciudad: **El Golf / Tobalaba (L1/L4)**, **Nueva Las Condes / Manquehue (L1)**, **Santiago Centro / Los Héroes (L1/L2/L3)** y **Plaza Egaña (L3/L4)**.

**Criterio de completitud:** Isócronas a pie y en auto detalladas por propiedad junto con la matriz de tiempos de viaje en Metro.

---

### Paso 5 — Estructura Financiera y Tabla de Amortización Cuota a Cuota

Modelar la estructura de financiamiento solicitada por el usuario (o aplicar el perfil estándar: **60% Pie / 40% Crédito a 5 años** con condiciones de mercado):

1. **Parámetros del Crédito:**
   * Monto de Pie inicial ($UF$ y moneda local).
   * Monto de crédito a financiar ($UF$ y moneda local).
   * Plazo ($n$ meses) y Tasa de Interés Anual Nominal ($i_{anual}$).
   * Carga Anual Equivalente ($CAE_{anual}$), incorporando seguros obligatorios (desgravamen, sismo e incendio) y gastos operacionales.
2. **Cálculo de Dividendos (Sistema Francés en UF y Moneda Local):**
   * Tasa mensual nominal: $r = (1 + i_{anual})^{1/12} - 1$.
   * Tasa mensual CAE: $r_{cae} = (1 + CAE_{anual})^{1/12} - 1$.
   * Dividendo base: $C = P \cdot \frac{r(1+r)^n}{(1+r)^n - 1}$.
   * Dividendo total con CAE (con seguros): $C_{cae} = P \cdot \frac{r_{cae}(1+r_{cae})^n}{(1+r_{cae})^n - 1}$.
3. **Tabla Comparada de Crédito:**
   * Resumen por propiedad con: Precio Total, Pie 60%, Crédito 40%, Dividendo Mensual CAE (UF y CLP) e Interés Total a pagar en los 5 años.
4. **Tabla de Amortización Mes a Mes (para análisis de unidad individual):**
   * Desglose de las 60 cuotas detallando: N° Cuota, Pago Mensual (CAE), Interés, Amortización Capital y Saldo Pendiente en UF y CLP.

**Criterio de completitud:** Modelación financiera exacta con dividendos y seguros calculados en UF y CLP.

---

### Paso 6 — Scorecard Multicriterio (0 a 10) y Dictamen de Ofertas

Calcular una calificación técnica ponderada de **0 a 10** para ordenar objetivamente las opciones:

| Dimensión | Ponderación | Criterios de Evaluación en Departamentos |
| :--- | :---: | :--- |
| **1. Ubicación y Metro** | **25%** | Distancia caminable a Metro troncal, isócronas y accesibilidad vehicular. |
| **2. Precio y Ratio UF/m²** | **25%** | Competitividad del ticket y descuento del ratio UF/m² vs. media comunal. |
| **3. Rentabilidad y Finanzas** | **20%** | Cap Rate neto, dividendo mensual sustentable y liquidez de reventa. |
| **4. Calidad, Terraza y Altura** | **15%** | Emplazamiento (piso 8+ / último piso), metraje de terraza, vista y luz. |
| **5. Seguridad y Calidad de Barrio** | **15%** | Entorno residencial seguro, áreas verdes y protección por Plan Regulador. |

* **Score Global = $\sum (\text{Nota} \times \text{Ponderación})$**

#### Hoja de Ruta de Visitas y Negociación:
* Ordenar las propiedades por Score Global decreciente.
* Definir para cada una el precio objetivo de oferta inicial (*target price*), margen de negociación y puntos críticos de inspección en terreno (aislación térmica en techos/ventanas, presión de agua, tablero eléctrico y actas de asambleas de copropiedad).

**Criterio de completitud:** Tabla de Scorecard completa con notas justificadas y flujograma de visitas con rangos de oferta.

---

### Paso 7 — Generación del Reporte HTML Autocontenido

Generar el documento HTML con diseño ejecutivo imprimible (`docs/reporte_cotizacion_[nombre_proyecto].html`) siguiendo el estándar de `/generate-html-doc`:

#### Requisitos de Scaffolding y Estilo:
- **Tipografía:** `Inter` (Google Fonts) para textos y `JetBrains Mono` para tablas numéricas.
- **Paleta de Color Ejecutiva:** Primario `#1a4369` (Azul Ejecutivo), Oscuro `#112c46`, Acento `#0369a1`, Éxito `#15803d`, Alerta `#b45309`.
- **Estructura Requerida:**
  1. *Botón Flotante de Impresión:* Clase `no-print` con `onclick="window.print()"`.
  2. *Encabezado con Metadatos 2x2:* Comunas, filtros, perfil financiero, rango de precios y fecha.
  3. *Tarjetas KPI (Grid de 4):* Cantidad de unidades, rango de UF/m², pisos/alturas y Scorecard máximo.
  4. *Matriz Comparativa Global (Tabla 1):* Columnas para #, Propiedad/Microzona, Tipología/Altura, Metraje, Precio UF (CLP), Ratio UF/m², Metro más cercano, Scorecard y botón **"Ver en Portal Inmob. ↗"** con enlace validado.
  5. *Auditoría Individual por Propiedad:* Tarjetas `.property-box` con subtítulo, enlace activo, descripción, grid de isócronas y pros/contras.
  6. *Matriz de Metro (Tabla 2):* Tiempos de viaje a polos estratégicos de la ciudad.
  7. *Simulación Financiera Comparada (Tabla 3):* Comparativa de pie, crédito, dividendos CAE e intereses.
  8. *Scorecard Ponderado (Tabla 4):* Desglose de las 5 dimensiones y nota final 0-10.
  9. *Flujograma de Negociación:* Bloques `.flow-step` numerados con prioridad de visita y ofertas.
  10. *Estilos `@media print`:* Márgenes A4, salto de página con `.page-break`, tablas expandidas y ocultamiento de botones de pantalla.

**Criterio de completitud:** Archivo HTML generado y verificado, libre de errores de JavaScript y con todos los enlaces externos dirigiendo a publicaciones activas reales.

---

## Checklist de Calidad antes de Entregar

- [ ] ¿Todas las URLs de las propiedades fueron probadas y responden con código HTTP 200 en el servidor?
- [ ] ¿Cada propiedad cuenta con su enlace directo e independiente (sin URLs duplicadas)?
- [ ] ¿Los departamentos cumplen con los filtros de piso (8+ o último piso), terraza y dormitorios/baños?
- [ ] ¿Se analizaron las isócronas a pie (10 y 20 min) y en auto (5, 15 y 30 min)?
- [ ] ¿Se incluye la matriz de tiempos de viaje en Metro a polos estratégicos de empleo y comercio?
- [ ] ¿La tabla financiera desglosa pie 60%, crédito 40%, dividendo mensual con CAE e intereses totales?
- [ ] ¿Se calculó el Scorecard multicriterio (0 a 10) con las 5 dimensiones ponderadas?
- [ ] ¿El reporte HTML es autocontenido, cuenta con botón de impresión y diseño responsivo?
