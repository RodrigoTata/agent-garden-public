# Matriz de Orquestación de Flujo: start-a-proyect

Esta matriz detalla las interacciones, entradas, salidas y habilidades complementarias que se activan según la naturaleza del proyecto.

---

## 1. Mapeo de Habilidades por Fase

| Fase | Habilidad Principal | Habilidades de Apoyo | Artefactos Entregables |
| :--- | :--- | :--- | :--- |
| **0. Clasificación & Setup** | `/repo-format` | N/A | Directorios `prototypes/`, `docs/`, `cad/`, `firmware/` |
| **1. Entrevista & Restricciones**| `/grill-with-docs` | `/research`, `/to-spec` | `docs/GLOSARIO_DOMINIO.md`, `docs/ADR-*.md`, `docs/spec.md` |
| **2. Gemelo Digital 3D** | `/interactive-3d-structure` | Three.js CDN | `prototypes/[proyecto]_3d.html` con brújula y cotas |
| **3. Cotización & Proveedores** | `/quotation-for` | `/business-implementation-plan` | `prototypes/[proyecto]_cotizacion.html` con Dual-Theme |
| **4. Manual e Instructivo** | `/generate-html-doc` | `/agile-prototype` | `prototypes/[proyecto]_manual.html`, `docs/version_log.md` |
| **5. Cierre & Navegación** | `start-a-proyect` | N/A | Barra de navegación bidireccional en todos los HTML |

---

## 2. Flujo Específico: Proyectos Físicos y de Construcción

*Ejemplos: Sombraderos, invernaderos, bancales elevados, estructuras de azotea, cobertizos.*

1. **Reconocimiento de Restricciones del Sitio**:
   - Orientación cardinal (Norte solar en hemisferio sur, Sur en hemisferio norte).
   - Altura de muros linderos y pretiles perimetrales.
   - Restricción de perforación: ¿Losa impermeabilizada? $\rightarrow$ Lastre gravitacional en chasis de base.
   - Aerodinámica de techumbre: Caída de agua orientada contra el viento dominante para generar efecto alerón (downforce).
2. **Modelado 3D (`/interactive-3d-structure`)**:
   - Descomposición paramétrica de escuadrías comerciales (ej. 2×4", 2×3", 1×2").
   - Aplicación de texturas de madera protegida con lasur, mallas técnicas translúcidas y herrajes metálicos.
   - Inclusión de silueta humana a escala (1.75 m) y cotas en metros.
3. **Cubicación y Cotización Local (`/quotation-for`)**:
   - Optimización de cortes para minimizar merma de listones comerciales de 3.2 m.
   - Comparación de opciones de mallas técnicas (60 Mesh monofilamento anti-trips vs. Raschel 50% vs. Aluminet).
   - Búsqueda en ferreterías y marketplaces locales (Mercado Libre, Sodimac, Easy).
4. **Instructivo de Montaje (`/generate-html-doc`)**:
   - Protocolo de seguridad y EPP (antiparras, guantes anticorte, protección auditiva).
   - Secuencia constructiva lógica (Chasis base $\to$ Pilares $\to$ Vigas $\to$ Arriostramientos $\to$ Tensado de mallas).
   - Lista de verificación de escuadra (regla 3-4-5) y torque.

---

## 3. Flujo Específico: Dispositivos IoT, Gadgets & Impresión 3D

*Ejemplos: Estaciones meteorológicas, sistemas de riego automatizado, monitores de cultivo con ESP32.*

1. **Definición Electrónica y Envolvente**:
   - Selección de microcontrolador (ESP32, RP2040, Arduino) y sensores (SHT31, DS18B20, higrómetros capacitivos).
   - Análisis de consumo eléctrico: Modo Deep Sleep, panel solar 5V/6V con batería LiFePO4/18650 o conexión a red.
2. **Investigación de Materiales (`/research`)**:
   - Selección de filamento para impresión 3D exterior:
     - **PETG**: Buena resistencia térmica y química, fácil impresión.
     - **ASA**: Máxima resistencia a rayos UV e intemperie exterior.
     - *Evitar PLA*: Degradación rápida bajo sol directo y deformación a >55°C.
3. **Modelado Espacial 3D (`/interactive-3d-structure`)**:
   - Representación de la carcasa, prensaestopas estancos (IP65/IP67), soporte a mástil y distribución de componentes.
4. **Cotización de Electrónica & Componentes (`/quotation-for`)**:
   - Proveedores especializados (Mercado Libre, Olimex, MCI Electronics, AliExpress si hay margen de tiempo).
5. **Manual de Ensamble y Programación (`/generate-html-doc`)**:
   - Diagrama de cableado / pinout de conexión.
   - Procedimiento de ensamblado mecánico con inserciones roscadas de latón (heat-set inserts M3).
   - Checklist de estanqueidad y pruebas de señal WiFi/LoRa.
