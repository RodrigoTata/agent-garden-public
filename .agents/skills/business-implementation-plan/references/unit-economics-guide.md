# Guía de Unit Economics y Costeo de Importación (Landed Cost)

Esta guía define las fórmulas canónicas y la estructura de costos unitarios para evaluar la viabilidad financiera de un negocio de importación, distribución o comercialización de productos físicos.

---

## 1. Estructura de Costo Total Puesto en Destino (Landed Cost)

El costo real de cada unidad puesta en bodega de destino no es solo el precio de compra en origen, sino la acumulación de 5 capas de costos:

```
[1. Costo FOB Origen] 
       + 
[2. Flete Internacional + Seguro (CIF)] 
       + 
[3. Aranceles e Impuestos de Importación] 
       + 
[4. Gastos Portuarios / Despacho Aduanero] 
       + 
[5. Almacenaje, Empaque y Logística Local]
       = 
[LANDED COST UNITARIO]
```

### Fórmulas de Cálculo:

1. **Costo FOB Unitario (Free on Board):**
   $$\text{FOB}_{\text{unit}} = \text{Precio de compra en origen} + \text{Flete interno origen hasta puerto/aeropuerto} + \text{Handling/Comisión de origen}$$

2. **Valor CIF (Cost, Insurance & Freight):**
   $$\text{CIF}_{\text{total}} = \text{FOB}_{\text{total}} + \text{Flete Internacional (Aéreo o Marítimo)} + \text{Seguro de Carga}$$

3. **Derechos Aduaneros e Impuestos (Caso Chile):**
   - **Arancel Ad-Valorem General:** $6\%$ sobre el valor CIF (revisar si aplica arancel 0% por Tratado de Libre Comercio / EPA Chile-Japón con Certificado de Origen).
   - **IVA de Importación:** $19\%$ sobre $(\text{Valor CIF} + \text{Ad-Valorem})$.
   *Nota:* Para personas jurídicas / empresas afectas a IVA, el IVA pagado en aduana constituye Crédito Fiscal (recuperable contra el IVA de las ventas), por lo que no es un costo de producto, sino una necesidad de capital de trabajo transitoria.

4. **Costos Fijos / Variables de Despacho e Internación:**
   - Honorarios Agente de Aduanas / Tramitación Courier.
   - Almacenaje fiscal / gastos de terminal aeroportuario o portuario.
   - Certificaciones especiales (ej. SEC para cargadores/fuentes de poder).

---

## 2. Margen de Contribución y Precios de Venta

Para cada canal de venta (B2C eCommerce, B2B Mayorista, Marketplaces), calcula:

$$\text{Margen Bruto Unitario (\$)} = \text{Precio de Venta Neto} - \text{Landed Cost Unitario}$$

$$\text{Margen Bruto (\%)} = \frac{\text{Margen Bruto Unitario}}{\text{Precio de Venta Neto}} \times 100$$

### Deducciones del Margen Operativo por Canal:
- **Comisión de Pasarela de Pago:** $2.5\% \text{ a } 3.5\% + \text{IVA}$ (Webpay / MercadoPago / Fintoc).
- **Comisión de Marketplace:** $10\% \text{ a } 16\% + \text{IVA}$ (MercadoLibre / Falabella / Ripley) si aplica.
- **Costo de Envío Última Milla (si es gratis para el cliente):** \$3.500 a \$6.000 CLP por paquete estándar.
- **Provisión por Garantía y Devoluciones:** Estimada en $2\% \text{ a } 4\%$ del ingreso neto.

---

## 3. Punto de Equilibrio (Break-Even Analysis)

$$\text{Unidades de Equilibrio} = \frac{\text{Costos Fijos Mensuales (Marketing, Bodega, Software, Salarios)}}{\text{Margen de Contribución Promedio por Unidad}}$$

Si el volumen de equilibrio supera la capacidad de financiamiento o la demanda estimada del canal para la fase piloto, el modelo requiere ajuste antes de invertir.
