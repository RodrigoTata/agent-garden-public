# 🎨 Paletas Ejecutivas de Formato Condicional para Excel

Guía de referencia de colores corporativos suaves (pasteles con alto contraste de texto) para evitar la fatiga visual y mantener una estética profesional en reportes y matrices.

---

## 1. Paleta de Ciclo de Vida y Estados (`Estado`)

| Estado / Concepto | Fill Hex | Font Hex | Negrita | Racionalidad |
| :--- | :---: | :---: | :---: | :--- |
| **Cerrado / Completado / Listo** | `#E2EFDA` | `#375623` | No | Verde suave tenue: éxito y cumplimiento. |
| **En curso / En progreso / Activo** | `#DDEBF7` | `#1F4E78` | **Sí** | Azul corporativo: foco activo de trabajo. |
| **Pendiente / Por iniciar / Pausado** | `#FFF2CC` | `#7F6000` | No | Amarillo claro: alerta preventiva sin alarma. |
| **Atrasado / Bloqueado / Rechazado** | `#FCE4D6` | `#C00000` | **Sí** | Rojo coral: alerta prioritaria de acción. |
| **Planificado / Futuro / Backlog** | `#F2F2F2` | `#595959` | No | Gris neutro: etapa fuera de ciclo inmediato. |
| **Descartado / Cancelado** | `#E7E6E6` | `#7F7F7F` | Tachado | Gris ceniza con texto tachado. |

---

## 2. Paleta de Criticidad y Urgencia (`Prioridad`)

| Nivel de Prioridad | Fill Hex | Font Hex | Negrita |
| :--- | :---: | :---: | :---: |
| **Crítica / Bloqueante** | `#FCE4D6` | `#C00000` | **Sí** |
| **Alta** | `#FFE6CC` | `#B25900` | No |
| **Media** | `#FFF2CC` | `#7F6000` | No |
| **Baja** | `#E2EFDA` | `#375623` | No |

---

## 3. Semáforo Temporal (`Días al Vencimiento`)

Aplicar sobre la fórmula de cálculo de días restantes respecto a hoy:

| Rango de Días | Fill Hex | Font Hex | Condición en Excel |
| :--- | :---: | :---: | :--- |
| **Vencido (`< 0`)** | `#FCE4D6` | `#C00000` | Celda `< 0` y `Estado <> "Cerrado"` |
| **Próximo a Vencer (`0` a `7`)** | `#FFF2CC` | `#7F6000` | Celda entre `0` y `7` y `Estado <> "Cerrado"` |
| **En Plazo (`> 7`)** | `#E2EFDA` | `#375623` | Celda `> 7` y `Estado <> "Cerrado"` |
| **Cerrado / No Aplica** | `#F2F2F2` | `#8C8C8C` | `Estado = "Cerrado"` |

---

## 4. Implementación en Python con openpyxl

```python
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.formatting.rule import CellIsRule

# Rellenos y Fuentes
fill_ok = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
font_ok = Font(color="375623", bold=False)

# Regla de formato condicional dinamico
ws.conditional_formatting.add(
    "J2:J200",
    CellIsRule(operator="equal", formula=['"Cerrado"'], fill=fill_ok, font=font_ok)
)
```
