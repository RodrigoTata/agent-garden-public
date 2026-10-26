# Lista de Verificación y Criterios Físicos: PHYSICAL-CHECKLIST

Referencia técnica para proyectos con solicitaciones estructurales, climáticas o de intemperie.

---

## 1. Criterios Aerodinámicos y Estabilidad

1. **Vientos Dominantes y Presión Dinámica**:
   - Calcular la presión de viento sobre paredes con mallas según su porosidad. Una malla 60 Mesh reduce el flujo en un 60-70%, transfiriendo una fuerza de empuje significativa a la estructura.
   - En techos a un agua, orientar la inclinación de tal forma que la arista baja apunte hacia la dirección de viento predominante, transformando el empuje horizontal en una fuerza descendente que estabiliza el chasis.
2. **Lastre Gravitacional vs. Anclajes**:
   - **Losa con impermeabilización**: Prohibida la perforación química o mecánica de hormigón. Emplear lastre húmedo distribuido (sustrato hortícola húmedo $\ge 1.000\text{ kg/m}^3$, adoquines o bidones).
   - Coeficiente de seguridad contra volcamiento: $\text{Momento estabilizador} \ge 1.5 \times \text{Momento de volcamiento}$.
3. **Aislamiento de Humedad y Drenaje**:
   - Separar maderas estructurales del suelo mediante tacos de neopreno de $\ge 10\text{ mm}$ o caucho reciclado para evitar pudrición por agua estancada.
   - Preservación de madera: Impregnación en autoclave (CCA) o impregnación superficial triple con Lasur microporoso fungicida/hidrorrepelente.

---

## 2. Criterios de Materiales y Durabilidad Exterior

| Material | Uso Recomendado | Resistencia UV / Intemperie | Consideraciones |
| :--- | :--- | :--- | :--- |
| **Pino Impregnado (2×4”, 2×3”)** | Chasis, pilares, soleras | Alta (10+ años exterior) | Verificar escuadría real (cepillado pierde ~5mm) |
| **Malla Anti-trips 60 Mesh (HDPE)** | Protección contra insectos y viento | Muy Alta (tratamiento UV) | Tensado con listón tapajunta o perfiles zig-zag |
| **Malla Raschel 50% / Aluminet** | Sombreado y control térmico | Alta | Aluminet refleja radiación IR mejor que polietileno negro |
| **Tornillos Spax / Drywall Fosfatado** | Fijación madera-madera | Media a Alta (preferir zincado/galvanizado) | Usar avellanado previo para no agrietar madera |
| **Filamento ASA (Impresión 3D)** | Carcasas IoT, soportes de sensores | Excelente (resistente a rayos UV y calor) | Requiere cámara cerrada o control térmico de cama |
| **Filamento PETG (Impresión 3D)** | Piezas estructurales semi-expuestas | Buena (soporta hasta 70°C y salinidad) | Flexible, no quiebra fácil bajo impacto |
| **Tornillería Inoxidable A2 / A4** | Enlaces expuestos a salinidad marina | Máxima (cero corrosión galvánica) | Imprescindible en zonas costeras |

---

## 3. Criterios de Ensamble y Tolerancias

1. **Verificación de Escuadra**:
   - Regla geométrica 3-4-5 (o 60cm - 80cm - 100cm) en todas las esquinas del chasis antes de fijar pilares.
   - Comprobar diagonales cruzadas del bastidor: la diferencia debe ser $\le 5\text{ mm}$.
2. **Arriostramiento Diagonal (Triangulación)**:
   - Todo cuadrilátero estructural requiere al menos una riostra o tornapunta a 45° en cada plano vertical para neutralizar deformaciones por cortante (racking).
3. **Tensión de Mallas Técnicas**:
   - Fijar primero la arista superior, luego estirar hacia abajo de manera uniforme antes de grapar o listonar los laterales.
   - En puertas enrollables, utilizar tubos contrapeso inferiores (ej. PVC hidráulico clase 10 de 32 mm) para mantener el paño extendido y resistir ráfagas.
