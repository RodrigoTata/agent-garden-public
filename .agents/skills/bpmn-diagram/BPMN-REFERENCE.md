# Referencia Camunda BPMN 2.0 & Plantilla HTML / XML

Este documento sirve como referencia para la construcción de diagramas de procesos siguiendo el estándar **BPMN 2.0 (OMG)** y la especificación de referencia de **Camunda**, empaquetados en visores interactivos HTML basados en `bpmn-js`.

---

## 1. Taxonomía de Elementos BPMN 2.0 (Camunda Standard)

### Eventos (Events)
- **Start Event** (`<bpmn:startEvent>`): Inicia el proceso. Círculo de línea fina.
  - *Tipos*: General, Mensaje (`<bpmn:messageEventDefinition>`), Temporizador (`<bpmn:timerEventDefinition>`), Señal, Condicional.
- **Intermediate Event** (`<bpmn:intermediateCatchEvent>` / `<bpmn:intermediateThrowEvent>`): Ocurre durante la ejecución. Círculo de doble línea.
  - *Tipos*: Mensaje, Temporizador (espera/delay), Escalación, Enlace (Link), Error.
- **End Event** (`<bpmn:endEvent>`): Finaliza el flujo o una rama. Círculo de línea gruesa.
  - *Tipos*: General (None), Mensaje, Error (`<bpmn:errorEventDefinition>`), Terminar (cancela todo el proceso: `<bpmn:terminateEventDefinition>`).

### Actividades / Tareas (Activities & Tasks)
- **User Task** (`<bpmn:userTask>`): Tarea ejecutada por un ser humano interactuando con un sistema.
- **Service Task** (`<bpmn:serviceTask>`): Operación automatizada por un servicio web, API o backend.
- **Script Task** (`<bpmn:scriptTask>`): Ejecución de script interno o lógica de código.
- **Send Task** (`<bpmn:sendTask>`) / **Receive Task** (`<bpmn:receiveTask>`): Envío/recepción explícita de mensajes.
- **Business Rule Task** (`<bpmn:businessRuleTask>`): Evaluación de tabla de decisiones (DMN) o reglas de negocio.
- **Manual Task** (`<bpmn:manualTask>`): Actividad física realizada sin apoyo de sistemas informáticos.
- **Sub-Process** (`<bpmn:subProcess>`): Secuencia de actividades encapsuladas dentro del proceso principal.

### Compuertas (Gateways)
- **Exclusive Gateway (XOR)** (`<bpmn:exclusiveGateway>`): Rombo con 'X'. Evaluación de condiciones donde **solo una** rama saliente es seleccionada.
- **Parallel Gateway (AND)** (`<bpmn:parallelGateway>`): Rombo con '+'. Divide el flujo en **todas** las ramas simultáneamente (fork) o espera a que todas terminen (join).
- **Inclusive Gateway (OR)** (`<bpmn:inclusiveGateway>`): Rombo con 'O'. Evalúa condiciones y activa **una o varias** ramas elegibles.
- **Event-Based Gateway** (`<bpmn:eventBasedGateway>`): Rombo con estrella/evento. El flujo continúa por la rama del primer evento que ocurra (ej: respuesta de mensaje vs timeout).

### Estructura de Contención y Conectores
- **Pool** (`<bpmn:participant>`): Entidad u organización independiente.
- **Lane** (`<bpmn:lane>`): Rol, departamento o actor dentro de un Pool.
- **Sequence Flow** (`<bpmn:sequenceFlow>`): Flecha sólida dentro del mismo Pool/Lane.
- **Message Flow** (`<bpmn:messageFlow>`): Flecha punteada con círculo inicial entre distintos Pools.
- **Data Object** (`<bpmn:dataObjectReference>`): Documento o conjunto de datos procesado.

---

## 2. Estructura de Coordenadas de Diagramación (BPMNDI)

Para que `bpmn-js` renderice el diagrama con la distribución adecuada:

| Elemento | Ancho (`width`) | Alto (`height`) | Spacing horizontal recomendado |
|---|---|---|---|
| **Event** | 36px | 36px | +140px |
| **Task / Activity** | 100px | 80px | +160px |
| **Gateway** | 50px | 50px | +140px |
| **Pool** | 800px - 1400px | 250px - 600px | - |
| **Lane** | Ancho del Pool | 200px por rol | - |

---

## 3. Plantilla Base de XML BPMN 2.0

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="false">
    <bpmn:startEvent id="StartEvent_1" name="Inicio">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="Task_1" name="Revisar Solicitud">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndEvent_1" name="Fin">
      <bpmn:incoming>Flow_2</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Task_1" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Task_1" targetRef="EndEvent_1" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="180" y="160" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1">
        <dc:Bounds x="270" y="138" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="430" y="160" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="216" y="178" />
        <di:waypoint x="270" y="178" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="370" y="178" />
        <di:waypoint x="430" y="178" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
```

---

## 4. Plantilla Contenedor HTML Interactivo (bpmn-js Viewer)

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Diagrama de Proceso BPMN 2.0</title>
  
  <!-- Estilos bpmn-js -->
  <link rel="stylesheet" href="https://unpkg.com/bpmn-js@17.11.1/dist/assets/bpmn-js.css">
  <link rel="stylesheet" href="https://unpkg.com/bpmn-js@17.11.1/dist/assets/diagram-js.css">
  <link rel="stylesheet" href="https://unpkg.com/bpmn-js@17.11.1/dist/assets/bpmn-font/css/bpmn.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

  <style>
    :root {
      --bg-primary: #0f172a;
      --bg-surface: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-hover: #0284c7;
      --border: #334155;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background-color: var(--bg-primary);
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: hidden;
    }

    header {
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border);
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 10;
    }

    .title-area h1 { font-size: 1.25rem; font-weight: 700; color: #fff; }
    .title-area p { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem; }

    .toolbar { display: flex; gap: 0.5rem; }
    .btn {
      background: #334155;
      color: #fff;
      border: 1px solid #475569;
      padding: 0.5rem 0.85rem;
      border-radius: 0.375rem;
      font-size: 0.85rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }
    .btn:hover { background: #475569; border-color: var(--accent); }
    .btn-primary { background: var(--accent); color: #0f172a; border: none; font-weight: 600; }
    .btn-primary:hover { background: var(--accent-hover); color: #fff; }

    #canvas-container {
      flex: 1;
      position: relative;
      background: #ffffff; /* Canvas claro para legibilidad BPMN estándar */
    }

    #canvas {
      width: 100%;
      height: 100%;
    }

    .bjs-powered-by { display: none !important; }
  </style>
</head>
<body>

  <header>
    <div class="title-area">
      <h1 id="diagram-title">Proceso de Negocio BPMN 2.0</h1>
      <p id="diagram-desc">Especificación interactiva del flujo de trabajo</p>
    </div>
    <div class="toolbar">
      <button class="btn" onclick="zoomIn()">🔍 Zoom +</button>
      <button class="btn" onclick="zoomOut()">🔍 Zoom -</button>
      <button class="btn" onclick="resetZoom()">🎯 Ajustar</button>
      <button class="btn btn-primary" onclick="exportSVG()">📥 Exportar SVG</button>
      <button class="btn" onclick="exportXML()">📄 Exportar XML</button>
    </div>
  </header>

  <div id="canvas-container">
    <div id="canvas"></div>
  </div>

  <!-- Visor interactivo BPMN-JS -->
  <script src="https://unpkg.com/bpmn-js@17.11.1/dist/bpmn-navigated-viewer.production.min.js"></script>

  <script>
    const bpmnXML = `<!-- BPMN 2.0 XML AQUI -->`;

    const viewer = new BpmnJS({
      container: '#canvas'
    });

    async function openDiagram(xml) {
      try {
        await viewer.importXML(xml);
        const canvas = viewer.get('canvas');
        canvas.zoom('fit-viewport');
      } catch (err) {
        console.error('Error al renderizar el diagrama BPMN:', err);
      }
    }

    function zoomIn() { viewer.get('canvas').zoom(viewer.get('canvas').zoom() * 1.2); }
    function zoomOut() { viewer.get('canvas').zoom(viewer.get('canvas').zoom() * 0.8); }
    function resetZoom() { viewer.get('canvas').zoom('fit-viewport'); }

    async function exportSVG() {
      try {
        const { svg } = await viewer.saveSVG();
        const blob = new Blob([svg], { type: 'image/svg+xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'diagrama-bpmn.svg';
        link.click();
      } catch (err) {
        console.error('Error exportando SVG:', err);
      }
    }

    async function exportXML() {
      try {
        const { xml } = await viewer.saveXML({ format: true });
        const blob = new Blob([xml], { type: 'application/xml' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'diagrama-bpmn.bpmn';
        link.click();
      } catch (err) {
        console.error('Error exportando XML:', err);
      }
    }

    openDiagram(bpmnXML);
  </script>
</body>
</html>
```
