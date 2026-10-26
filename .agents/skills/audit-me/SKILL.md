---
name: audit-me
description: Ejecuta una auditoría crítica, implacable y exhaustiva sobre cualquier propuesta, lógica de negocio, arquitectura de dominio, plan operativo, idea o desarrollo de software. Úsala cuando el usuario pida auditar, criticar, buscar fallas lógicas, someter a estrés un diseño, evaluar la lógica de negocio en código o mencione "audit-me", "auditar", "análisis crítico", "criticar lógica" o "stress test".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Audit Me: Auditoría Crítica y Stress-Testing de Lógica y Arquitectura

Esta skill somete cualquier artefacto, idea, plan, arquitectura o código a una **auditoría crítica implacable**. Su meta no es validar ni adular, sino **desmontar supuestos frágiles**, descubrir **invariantes rotos**, identificar **puntos ciegos operacionales** y anticipar **fricciones del mundo real** antes de que cuesten dinero, tiempo o continuidad operativa.

---

## Leading Words

- **Quirúrgico**: Crítica directa, fundamentada y sin eufemismos ni complacencia. Señala con exactitud el archivo, línea, regla o entidad defectuosa y el mecanismo exacto por el cual falla.
- **Invariante**: Verdad irrenunciable del negocio o sistema que jamás debe romperse bajo ningún estado (ej. *"un conductor en descanso no puede salir a ruta sin devengar horas extra"*). Si un invariante es violable, la arquitectura tiene una falla crítica.
- **Stress-Test**: Evaluación bajo condiciones hostiles y de borde: volumen extremo, concurrencia, actores negligentes o maliciosos, cortes de red, y desviaciones de la realidad operativa frente al "happy path".
- **Leakage (Fuga de Dominio)**: Contaminación de fronteras donde las reglas de negocio quedan dispersas en capas técnicas (controladores, UI, consultas ad-hoc) o conceptos de infraestructura infectan el modelo conceptual.

---

## Modos de Auditoría (Branches)

Identifica el objeto principal de la auditoría y aplica el lente correspondiente:

1. **Lógica de Negocio y Operaciones**: Planes comerciales, SLAs, incentivos, márgenes, flujos operativos físicos (ej. andenes, transporte, plantas).
2. **Lógica de Arquitectura y Datos**: Modelos entidad-relación (DER), dominios, esquemas de persistencia, acoplamiento inter-módulo, integridad referencial y cascadas.
3. **Ideas, Estrategia y Planes**: Propuestas de proyecto, roadmaps, cartas Gantt, supuestos de adopción y viabilidad financiera/logística.
4. **Desarrollo de Software (Lógica-Lógica de Negocio)**: Implementación en código, clases de dominio, servicios, máquinas de estado y contratos de API contra las reglas puras del negocio. *(Consulta [references/software-business-logic.md](references/software-business-logic.md))*.

---

## Steps

Ejecuta estos pasos en secuencia estricta. No avances sin verificar el criterio de completitud.

### 1. Encuadre y Extracción de Invariantes
- Lee exhaustivamente el material objetivo (documentos de dominio, diagramas, esquemas, código fuente o propuesta).
- Identifica el objetivo declarado y extrae formalmente:
  - **Invariantes Obligatorios**: ¿Qué reglas o restricciones deben cumplirse el 100% de las veces?
  - **Supuestos Implícitos**: ¿Qué da por sentado el autor que podría no ser cierto en la realidad? (ej. red siempre disponible, actores honestos, datos completos, tiempos de traslado teóricos).
  - **Métricas de Éxito / Margen**: ¿Cómo impacta el diseño en el costo, SLA, rentabilidad o riesgo legal?
- **Completion criterion**: Lista explícita y numerada de al menos 4 a 6 invariantes y supuestos clave extraídos del material bajo auditoría.

---

### 2. Prueba de Estrés Multidimensional (Stress-Testing)
Somete el artefacto a cuatro pruebas de choque deliberadas:

1. **La Prueba del Actor Perezoso / Tramposo (Perverse Incentives)**:
   - ¿Qué atajos tomará un operador, conductor, cliente o usuario si el sistema se lo permite para ahorrarse trabajo o ganar más dinero?
   - ¿El diseño premia o castiga el reporte veraz de contingencias?
2. **La Prueba de la Fricción del Mundo Real (Real-World Chaos)**:
   - ¿Qué ocurre ante averías simultáneas, cortes de carretera, atrasos de proveedores, emergencias climáticas o documentos vencidos en mitad de faena?
   - ¿El sistema se bloquea por completo o degrada con gracia (*graceful degradation*)?
3. **La Prueba del Volumen y Concurrencia (Race Conditions)**:
   - ¿Qué pasa si dos operadores reasignan el mismo recurso (camión, máquina, lote) en el mismo segundo?
   - ¿Existen estados zombis o inconsistencias de estado temporal?
4. **La Prueba del Margen y Costo Invisible (Financial & Operational Bleed)**:
   - ¿Dónde se generan sobrecostos ocultos no computados? (ej. horas extra no trazadas, multas contractuales de clientes, consumo de combustible, penalizaciones).
- **Completion criterion**: Registro documentado del comportamiento del sistema ante cada una de las 4 pruebas de choque, identificando puntos de ruptura o vulnerabilidades.

---

### 3. Ejecución del Lente Especializado: Software desde la Lógica de Negocio
*(Aplica cuando el objetivo incluya especificación técnica, modelos de base de datos o código fuente).*

Revisa el artefacto contra los 5 pilares de lógica de negocio en software:
- **Pureza de la Entidad de Dominio**: ¿La entidad de negocio modela reglas reales o es una bolsa anémica de datos (*Anemic Domain Model*) con lógica desparramada en vistas o controllers?
- **Completitud y Clausura de Estados**: ¿El espacio de estados es exhaustivo? ¿Se previenen transiciones ilegales (ej. un viaje cancelado pasando a cerrado)?
- **Invariantes en Memoria vs Restricciones de BD**: ¿Las reglas de negocio se defienden antes de golpear la base de datos o dependen de errores SQL genéricos?
- **Inmutabilidad de Líneas Base**: ¿Al alterar un plan o reasignar una entidad en marcha, se conserva el snapshot histórico original para medir desviaciones de KPI?
- **Manejo de Errores y Degradación**: ¿Los errores de negocio (ej. conductor inhabilitado) se capturan explícitamente o caen en catch-alls silenciosos?
- *Para profundizar en patrones de código, anti-patrones y checklist quirúrgico, consulta:* [references/software-business-logic.md](references/software-business-logic.md).
- **Completion criterion**: Evaluación punto por punto de cada pilar de lógica de negocio aplicada al software o esquema bajo revisión.

---

### 4. Veredicto y Redacción del Reporte de Auditoría
Genera un informe estructurado que categorice los hallazgos según su severidad:

- **Veredicto General**:
  - `ROBUSTO`: Cumple con los invariantes y resiste el estrés operacional.
  - `CONDICIONAL`: Requiere ajustes en bordes y mitigación de supuestos.
  - `FRÁGIL`: Presenta fugas de margen, riesgos de bloqueo operacional o inconsistencias de estado.
  - `FALLA CRÍTICA`: Invariantes fundamentales rotos; inviable en producción sin rediseño mayor.
- **Matriz de Invariantes**: Tabla con el estado de cada invariante (`Vigente`, `En Riesgo`, `Roto`).
- **Hallazgos Detallados Clasificados por Severidad**:
  - 🔴 **Crítico (P0)**: Rompe el negocio, genera fraude, multas legales, pérdida de datos o bloquea la operación.
  - 🟠 **Mayor (P1)**: Degrada severamente el margen, falsea métricas o genera trabajo manual excesivo.
  - 🟡 **Moderado (P2)**: Ambigüedad en reglas de borde, acoplamiento innecesario o falta de trazabilidad.
  - 🟢 **Oportunidad de Mejora (P3)**: Refinamiento de nomenclatura, simplificación conceptual o optimización menor.
- **Plan Quirúrgico de Remediación**: Acciones concretas, priorizadas e inmediatas para blindar el diseño.
- **Completion criterion**: Reporte completo presentado al usuario o guardado en el archivo correspondiente con veredicto, matriz de invariantes, hallazgos priorizados y remediaciones accionables.

---

## Failure Modes

- **Complacencia (Sycophancy)**: Decir "está muy bien estructurado" en lugar de buscar activamente dónde fallará el diseño. *Cura: Asumir que todo diseño humano tiene al menos 2 debilidades operacionales u ocultas y encontrarlas.*
- **Foco Técnico Superficial**: Centrarse en estilo de código, formato o sintaxis ignorando si la regla de negocio tiene sentido en la vida real. *Cura: Ejecutar siempre la Prueba de la Fricción del Mundo Real.*
- **Crítica Vaga o Inaccionable**: Decir "podría fallar ante atrasos" sin indicar la regla, entidad o fórmula que lo produce. *Cura: Ser quirúrgico; vincular cada crítica a un invariante específico y sugerir la solución puntual.*
- **Ceguera del Happy-Path**: Asumir que los operadores seguirán el protocolo ideal sin desviarse jamás. *Cura: Aplicar la Prueba del Actor Perezoso.*
