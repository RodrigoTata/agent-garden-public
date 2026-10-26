# Modelo de alta calidad con /three-js

`/three-js` reconstruye el objeto como modelo Three.js procedural fiel a una imagen: forma orgánica, materiales y detalle que el gemelo de `interactive-3d-structure` no busca. El gemelo responde **cuánto mide**; el modelo de alta calidad, **cómo se ve**.

## Antes de empezar

- **Costo:** el gemelo cuesta unos pocos miles de tokens; `/three-js` cuesta del orden de 80 000 a 180 000 por objeto (más en personajes), sobre todo en ciclos de revisión. Si el humano no lo pidió explícitamente, dile el costo y confirma antes de seguir.
- **Requisitos:** al menos una imagen del objeto (en la entrada **texto** esta ruta no aplica) y Python 3.10+. En Windows, `python3` puede ser el alias de la Microsoft Store que no ejecuta nada: usa `python` o `py -3`.
- **El gemelo va primero.** Su `verify.mjs` en `VERDE` prueba que el inventario es coherente; `/three-js` parte de ese inventario, nunca de medidas nuevas.

## Traspaso

Sigue el `SKILL.md` de `/three-js` completo, con estas entradas del escaneo:

- **Imagen de referencia:** la imagen de producto o foto con el objeto completo, de frente o en oblicua, con el fondo más limpio y anclada con control ✓. Las demás vistas van como vistas adicionales.
- **Dimensiones:** `/three-js` trabaja en unidades relativas. Al autorar su spec, el `dimensions` de cada componente es su medida del inventario dividida por la mayor medida total del objeto, y su `confidence` sale de la fuente:

  | Fuente | `confidence` |
  |---|---|
  | `medido` | 0.95 |
  | `foto ✓`, `ficha` | 0.85 |
  | `catálogo` | 0.8 |
  | `foto` | 0.6 |
  | `supuesto` | 0.3 |

- **Rasgos que definen la identidad:** las piezas del inventario con su cantidad y uniones; los materiales de la ficha o de la foto van como evidencia de material.

## Medidas en conflicto

Si una revisión de `/three-js` pide cambiar una proporción, el inventario manda. Solo una medida `foto` o `supuesto` puede cambiar, y el cambio vuelve al paso 3 del escaneo (pregunta) o al 5 (contraste), y de ahí al inventario, al `.spec.js` y al gemelo. Nunca corrijas una medida solo en el modelo de alta calidad.

*Completo cuando*: el gemelo está en `VERDE`, `/three-js` cerró su propia lista de control (su `next.py` sin pasos pendientes) y cada dimensión del modelo sale del inventario.
