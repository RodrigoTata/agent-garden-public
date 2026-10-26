---
name: frontend-analysis
description: Analiza y mapea una interfaz compleja (tipo Cockpit o Digital Twin) y genera una guía visual interactiva en formato HTML. Úsalo cuando el usuario pida analizar cómo funciona un frontend, dónde está cada componente o genere una guía visual de navegación.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# frontend-analysis

Esta skill transforma el mapeo abstracto de una interfaz compleja (tipo Cockpit o Digital Twin) en un **Documento HTML Interactivo y Premium**. En lugar de ser solo una referencia en texto, la skill genera un entregable visual listo para usarse en el navegador.

## Steps

Ejecuta estos pasos de manera secuencial para garantizar un resultado predecible y de alta calidad estética:

### Step 1 — Mapeo de la Estructura (Information Hierarchy)
Analiza la interfaz objetivo (si no se especifica, pregunta cuál es la interfaz objetivo) e identifica los 5 pilares fundamentales del **Cockpit**:
1. **Spatial View (Diseño 3D)**: Ubicación espacial, modelos 3D interactivos, colisiones.
2. **Tabular Equipment (Equipamiento)**: Tablas de datos crudos, edición de coordenadas exactas y parámetros de consumo.
3. **Logic Flow (Lógica)**: Editor visual de nodos, reglas de automatización y triggers.
4. **Telemetry Cockpit (Monitoreo)**: Gráficos de tiempo real (VPD, temperatura), deslizadores de prueba.
5. **AI Traceability (Bitácora)**: Logs históricos, recomendaciones agronómicas de IA.

*Completion criterion:* Tienes la información clara de "dónde está" y "cómo funciona" cada pilar.

### Step 2 — Scaffold del Documento HTML (Design System)
Construye un archivo `.html` único e independiente (todo el CSS inline). Debes usar una estética **Oscura, Vibrante y Premium** (Glassmorphism, bordes sutiles, fuentes modernas como Inter):
- **Fondo base**: Oscuro profundo (`#0A0A0A` o `#111827`).
- **Acentos**: Cian o Esmeralda (`#10B981`) para títulos y botones.
- **Tipografía**: Importa `Inter` desde Google Fonts.
- **Componentes**: Diseña tarjetas (`.card`) para cada pilar, usando `backdrop-filter: blur()` y `border: 1px solid rgba(255,255,255,0.1)`.

*Completion criterion:* La estructura HTML base con el bloque `<style>` premium está armada en memoria.

### Step 3 — Inserción de Contenido
Rellena el documento HTML. Por cada pilar identificado en el Step 1, crea una tarjeta (`.card`) que contenga:
- **Icono / Título**: El nombre de la vista.
- **Ruta de Navegación**: Dónde hacer clic (ej. *Sidebar -> Diseño 3D -> Lógica*).
- **Mecánica**: Explicación técnica (ej. *Lienzo WebGL drag-and-drop*).
- **Caso de Uso**: ¿Para qué va el usuario a esta pantalla?

*Completion criterion:* El HTML está completo, no tiene secciones vacías y refleja la jerarquía de información.

### Step 4 — Guardado y Ejecución
1. Utiliza `write_to_file` para guardar el archivo como `[nombre-proyecto]_frontend_analysis.html` en el directorio raíz o en `docs/`.
2. Utiliza `run_command` para abrir el archivo directamente en Chrome (ej. `Start-Process chrome "ruta\al\archivo.html"`).
3. Finaliza reportando al usuario que la guía interactiva ha sido generada y abierta.

*Completion criterion:* El archivo está guardado y el comando del navegador fue ejecutado con éxito.

## Failure Modes
- **Diseño Básico**: Entregar un HTML blanco con texto negro sin estilos. Esta skill exige una estética **Premium Cockpit**.
- **Sedimentación**: Generar secciones vacías que no aplican a la interfaz que se está analizando. Si el frontend no tiene vista 3D, omite ese pilar.
