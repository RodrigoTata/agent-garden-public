---
name: interactive-3d-structure
description: Construye gemelos digitales 3D en un solo HTML (Three.js) que abren en cualquier navegador, escritorio o móvil. Usar cuando el usuario pida ver en 3D una estructura o cubicación de madera, un gabinete o prototipo de hardware, la disposición física de un montaje (estanques, macetas, mangueras), cuando un visor 3D existente carga en blanco o le faltan cotas, capas u orientación, o cuando /3d-scanner u otra skill entrega un inventario de medidas.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Gemelo digital 3D

Un **gemelo digital** es un `.html` único armado sobre [template.html](template.html): el motor ya viene probado (Three.js fijado, cámaras, capas, cotas, gizmo, ficha por pieza, rayos X, vista explosionada, tema claro/oscuro, PNG, impresión, aviso si falta WebGL o red). Tú escribes solo el **SPEC**, los datos del objeto, en `<visor>.spec.js`; `armar.mjs` lo inyecta en la plantilla. Nunca escribes un visor desde cero, nunca lees ni editas `template.html` ni el `.html` armado: el `.spec.js` es lo único que se toca.

El SPEC es la **fuente única** del visor: toda medida visible (cota, ficha, leyenda, aviso) sale de una constante del SPEC. Un número escrito dos veces termina contradiciéndose. Caso real: un visor decía 30 L en la leyenda y 60 L en un comentario, y su geometría medía 78 L.

## Inventario

El inventario es el contrato de entrada: `<visor>.inventario.md`, junto al visor. Lo escribe quien trae las medidas (`/3d-scanner`, otra skill o tú en el paso 1), y un cambio de medida entra siempre por aquí antes de llegar al `.spec.js`.

```markdown
# Inventario — Mesa de centro BORGEBY
Origen: 3d-scanner (web + fotos)

| Pieza | Tipo | Campo | mm | Fuente | Nota |
|---|---|---|---|---|---|
| Cubierta | cilindro | diam | 699 | ficha | ficha: 27 1/2" |
| Cubierta | cilindro | alto | 18 | supuesto | tablero estándar |

## Contradicciones
- Alto total: ficha 419 mm, foto ≈ 450 mm (+7 %). Se usa ficha.

## Avisos
- info: Escaneado desde 6 imágenes de la ficha web; medidas `foto` ±10 %.
```

- **Fuente:** de dónde sale el número (mensaje del usuario, BOM, datasheet, documento del repo, visor anterior, o las fuentes de `/3d-scanner`). Sin fuente, `supuesto` con el criterio en la nota.
- **Al SPEC:** la fuente de cada fila va a la `nota` de su pieza; las filas `supuesto` se listan en un aviso `alerta`; cada línea de `## Avisos` entra tal cual a `avisos`.

## Pasos

### 1. Inventario
Si existe `<visor>.inventario.md` (lo dejó `/3d-scanner` u otra skill), léelo y pasa al paso 2 sin rehacerlo. Si no, escríbelo: cada pieza con sus medidas en **mm** y la fuente de cada número; si dos fuentes discrepan, anota ambas en `## Contradicciones` y elige una.

Si partes de un visor existente, lee antes [MIGRAR.md](MIGRAR.md): sus unidades, leyendas y rutas de carga no son confiables.

*Completo cuando*: cada pieza tiene todas sus medidas con fuente o `supuesto` y cada contradicción está listada.

### 2. SPEC
Lee [SPEC.md](SPEC.md) (tipos de pieza, convenciones —mm, `pos` = centro de la base—, materiales y ejemplos por dominio) y escribe `<visor>.spec.js`: las constantes y `const SPEC = { … };`, lo que va entre `SPEC:INICIO` y `SPEC:FIN`. Luego arma:
```
node <carpeta de esta skill>/scripts/armar.mjs <visor>.spec.js
```
- Cada medida del inventario va en una constante con nombre. Piezas, cotas y textos la usan (`${}` en los textos) y nunca repiten el número.
- Cada pieza que debe caber dentro de otra (componente en gabinete, bomba en estanque) lleva `dentroDe`, y el motor comprueba el calce.
- Si una forma no se arma con los tipos, se resuelve con `constructores` (SPEC.md § Constructores), no editando el motor.
- Para cambiar un visor ya armado, edita su `.spec.js` y vuelve a armar. Si solo existe el `.html`, `armar.mjs --extraer <visor>.html` recupera el `.spec.js`.

*Completo cuando*: cada fila del inventario tiene su constante, cada número visible viene de una constante y `armar.mjs` imprimió la ruta del visor.

### 3. Verde
```
node <carpeta de esta skill>/scripts/verify.mjs <visor.html>
```
El script abre el visor en Chrome o Edge headless, en escritorio (1280×800, recorriendo toda la interfaz) y en móvil (390×844). Queda **verde** solo si hay cero errores de consola o de red, todas las piezas construidas, el SPEC sin errores (incluidos los calces `dentroDe`), el modelo visible en el encuadre y sin scroll horizontal. Si queda rojo, corrige el `.spec.js`, vuelve a armar y repite.

Después abre las capturas cuyas rutas imprime el script (escritorio, móvil y tras la interacción) y contrástalas con el inventario: cada pieza donde corresponde, nada flotando ni atravesado, lo importante a la vista en la vista inicial y cotas legibles sin encimarse.

*Completo cuando*: verify imprime `VERDE` y revisaste las tres capturas. Si falta Chrome/Edge o red, el visor **no está verificado**, y así se informa.

### 4. Entrega
Si el inventario dice `Origen: 3d-scanner`, no entregues: vuelve al paso 5 (Contrastar) de esa skill, que hace la entrega. Si no, informa la ruta del visor, la de su `.spec.js` e inventario, qué se verificó (navegador y tamaños), los supuestos y las contradicciones del inventario.
