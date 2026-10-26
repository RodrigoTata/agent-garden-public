---
name: bpmn-diagram
description: Genera diagramas de procesos de negocio BPMN 2.0 en HTML interactivo utilizando bpmn-js (Camunda reference). Usar cuando el usuario pida diagramar un proceso de negocio, un flujo BPMN, especificación de proceso o workflow.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# BPMN Process Diagram Generator

Genera diagramas de procesos de negocio limpios, estandarizados e interactivos en formato **BPMN 2.0 (OMG)** bajo la especificación de referencia de **Camunda**, empaquetados en un archivo HTML ejecutable en cualquier navegador mediante `bpmn-js`.

---

## Process

### Step 1 — Process Analysis & BPMN Element Mapping
Analiza el proceso solicitado para modelar sus límites, actores y flujo lógico:
1. **Identificar Pools y Lanes**: Determina las organizaciones o roles participantes (ej. *Cliente*, *Sistema Backend*, *Aprobador*).
2. **Mapear Eventos**:
   - *Start Event*: Detonante del proceso (Inicio por tiempo, mensaje o acción manual).
   - *Intermediate Events*: Pausas, recepción/envío de mensajes o temporizadores.
   - *End Event*: Resultado final (Éxito, Error o Terminación explícita).
3. **Mapear Actividades**: Clasifica las tareas según la taxonomía Camunda (*User Task*, *Service Task*, *Script Task*, *Business Rule Task*, *Sub-Process*).
4. **Mapear Compuertas (Gateways)**:
   - *Exclusive (XOR)*: Decisión única entre ramas mutuamente excluyentes.
   - *Parallel (AND)*: División o unión de ramas simultáneas.
   - *Inclusive (OR)*: Una o varias condiciones válidas.
   - *Event-Based*: Elección dictada por el primer evento recibido.

Consulta la taxonomía completa en [BPMN-REFERENCE.md](BPMN-REFERENCE.md).

*Completion criterion*: Mapeo en memoria de todos los nodos, actores y flujos de secuencia con sus correspondientes tipos de elemento BPMN 2.0.

---

### Step 2 — BPMN 2.0 XML Generation & Layout
Genera la especificación XML estandarizada BPMN 2.0 junto con las coordenadas de diagramación en `bpmndi`:
1. **Estructura XML**: Construye `<bpmn:definitions>`, `<bpmn:collaboration>` (si existen Pools/Lanes) o `<bpmn:process>`.
2. **Conexiones**: Define `<bpmn:sequenceFlow>` para flujos internos y `<bpmn:messageFlow>` para intercambio entre Pools.
3. **Coordenadas de Diagramación (BPMNDI)**:
   - Asigna coordenadas `dc:Bounds` (x, y, width, height) para cada forma (`bpmndi:BPMNShape`).
   - Define puntos de trayectoria `di:waypoint` para las conexiones (`bpmndi:BPMNEdge`).
   - Mantén un espaciado horizontal constante de ~160px entre actividades y distribuye las líneas verticalmente por Lane (~200px por Lane).

*Completion criterion*: String XML válido y bien formado acorde al esquema BPMN 2.0 de la OMG con bloque `bpmndi:BPMNDiagram` completo.

---

### Step 3 — Construct Standalone Interactive HTML
Empaqueta el XML generado dentro de una página HTML autónoma interactiva basada en `bpmn-js`:
1. Incluye las librerías CDN de `bpmn-js` (`bpmn-navigated-viewer.production.min.js` y sus hojas de estilo CSS).
2. Diseña un encabezado limpio con el título del proceso, descripción breve y barra de herramientas:
   - Botones de **Zoom In**, **Zoom Out** y **Fit View**.
   - Botones de exportación: **Descargar SVG** y **Descargar XML**.
3. Incrusta el XML generado en la variable de inicialización del visor `viewer.importXML(bpmnXML)`.
4. Añade manejo responsivo (`window.onresize`) para ajustar el visor automáticamente al tamaño de la pantalla.

Usa la plantilla HTML disponible en [BPMN-REFERENCE.md](BPMN-REFERENCE.md).

*Completion criterion*: Código HTML completo guardado mediante `write_to_file` en `<nombre_proceso>_bpmn.html`.

---

### Step 4 — Verification & Delivery
1. Verifica que el archivo HTML sea sintácticamente válido y no contenga etiquetas desparejadas o caracteres XML sin escapar (`&`, `<`, `>`).
2. Confirma que la interfaz incluya todos los controles interactivos y que la versión CDN utilizada de `bpmn-js` sea funcional.
3. Presenta al usuario el enlace de archivo local (`file:///...`) para su apertura en el navegador.

*Completion criterion*: Archivo `.html` existente en el sistema de archivos listo para su visualización interactiva.

---

## Failure Modes

- **Solapamiento de Nodos (Zero Coordinates)**: Omitir las coordenadas en `bpmndi:BPMNShape` provoca que los elementos se encamen en la esquina (0,0). *Solución*: Asignar siempre valores `dc:Bounds` incrementales (x += 160) según la secuencia lógica.
- **XML mal formado por caracteres especiales**: Usar `<` o `>` dentro de los atributos `name` de las tareas rompe la sintaxis XML. *Solución*: Reemplazar con entidades XML (`&lt;`, `&gt;`, `&amp;`).
- **CDN no disponible o bloqueado**: Asegurar que las URLs de `unpkg.com` apunten a la versión LTS estable de `bpmn-js@17.11.1`.
