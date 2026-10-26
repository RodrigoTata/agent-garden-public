---
name: web-audit
description: Ejecuta una ingeniería inversa y auditoría profunda (técnica, estética, UX/UI) de una página web, interactuando de forma natural (sigilosa).
license: Apache-2.0
metadata:
  author: Rodrigo González
---

Esta skill ejecuta un **Análisis Profundo** y una **Ingeniería Inversa** sobre una página web objetivo. El propósito es desentrañar su funcionamiento técnico, su lógica de negocio y su propuesta estética interactuando de manera natural, generando un reporte **Exhaustivo** con críticas y recomendaciones de alto nivel.

## Leading Words

- **Exhaustivo**: El reporte no deja piedra sin remover. Abarca dimensiones técnicas, estéticas, lógicas y de UX/UI, profundizando en cada aspecto.
- **Sigiloso**: Las interacciones del subagente de navegador simulan el comportamiento humano real (pausas, scroll gradual, lectura simulada) para evadir sistemas de detección de bots y experimentar la interfaz como un usuario genuino.
- **Quirúrgico**: Las críticas y recomendaciones van directo al punto, están fundamentadas en estándares de la industria y no tienen ambigüedades.

## Steps

Ejecuta estos pasos en orden para garantizar la **Previsibilidad**. No avances al siguiente paso hasta cumplir el **Completion criterion** del actual.

1. **Reconocimiento Sigiloso**:
   - Inicia un `browser_subagent` con instrucciones estrictas de ser **Sigiloso**.
   - Proporciona al subagente la URL y pídele que explore la página, interactúe con los elementos principales (menús, botones, modales) y evalúe la estética y la experiencia de uso.
   - El subagente debe observar la estructura del DOM, posibles frameworks utilizados y el comportamiento reactivo de la interfaz.
   - **Completion criterion**: El subagente ha finalizado su exploración sin ser bloqueado, retornando un resumen detallado de la estructura, tecnologías, flujo y estética de la página.

2. **Ingeniería Inversa**:
   - Consolida la información obtenida. Deduce el stack tecnológico (React, Vue, Tailwind, etc.), patrones de diseño (ej. micro-servicios de frontend, SSR vs CSR) y la lógica de negocio subyacente.
   - Identifica fricciones en el recorrido del usuario, fallas de diseño, aciertos estéticos y decisiones arquitectónicas.
   - **Completion criterion**: Existe un mapa mental estructurado que desglosa cómo y por qué la página está construida y diseñada de esa manera.

3. **Redacción del Reporte Exhaustivo**:
   - Crea un artifact Markdown (ej. `reporte_auditoria_web.md`) estructurado según las dimensiones solicitadas por el usuario (o por defecto: Técnico, Estético, Lógico/Negocio, UX/UI).
   - Sé **Quirúrgico**: Critica de forma constructiva pero directa, y provee recomendaciones de alto nivel para superar el diseño o la técnica actuales (ej. sugiriendo micro-interacciones, mejoras de accesibilidad, rediseño de jerarquías).
   - Utiliza alertas (Alerts de GitHub) para marcar vulnerabilidades o áreas críticas de mejora.
   - **Completion criterion**: El artifact del reporte ha sido creado, abarcando todas las áreas con profundidad y rigor técnico/estético, y se ha presentado al usuario.

## In-skill Reference: Dimensiones del Análisis

Cuando redactes el reporte, asegúrate de cubrir estas dimensiones si el usuario no especificó un enfoque distinto:

- **Técnica**: Análisis del DOM, suposición de tecnologías, optimización de carga percibida, estructura semántica del HTML y accesibilidad.
- **Estética**: Paleta de colores, tipografía, jerarquía visual, uso del espacio (white space), sensación "premium" y consistencia del sistema de diseño.
- **Lógica / Negocio**: Eficacia del embudo de conversión, llamadas a la acción (CTAs), claridad de la propuesta de valor y arquitectura de la información.
- **UX/UI**: Fricciones en la interacción, comportamiento de modales, estados de hover/focus, y fluidez general de la experiencia.
