# Migrar un visor 3D existente

Un visor viejo es una **fuente de medidas poco confiable**, no una base de código: no se parcha. Se extraen sus medidas al inventario y se reconstruye sobre la plantilla, conservando la ruta y el nombre del archivo porque otros documentos lo enlazan: escribe `<visor>.spec.js` junto a él y arma con `armar.mjs <visor>.spec.js --reemplazar`.

Si el visor ya salió de la plantilla (tiene los marcadores `SPEC:INICIO` y `SPEC:FIN`), no es una migración: `armar.mjs --extraer <visor>.html` saca su SPEC a `<visor>.spec.js` y desde ahí se edita.

## Trampas que dejan la pantalla en blanco

| En el HTML viejo | Qué pasa |
|---|---|
| `…/examples/js/controls/OrbitControls.js` | 404 desde r148 → `THREE.OrbitControls is not a constructor` → escena vacía. |
| `…/build/three.min.js` o `three.js` (UMD) | 404 desde r161 (r150–r160 solo avisaban). |
| Núcleo y addons de versiones distintas | Controles muertos o errores sutiles. |
| `<script type="module" src="./algo.js">` | Chrome lo bloquea al abrir con doble clic (`file://`, CORS). Todo va inline. |
| Sin pantalla de fallo | Cuando falta WebGL 2 (requerido desde r163) o red, el usuario ve negro y no sabe por qué. |
| `THREE.PCFSoftShadowMap`, `THREE.Clock` | Eliminado u obsoleto en r186 (solo avisos). |
| `scene.rotation.y += …` como autogiro | La brújula y las vistas dejan de corresponder al modelo. |
| `100vh`, `backdrop-filter` sin `-webkit-`, `devicePixelRatio` sin tope | Recortes y lentitud en iPhone/Safari. |

Para detectarlas: `grep -nE "examples/js|three(\.min)?\.js|three@|three\.js/r[0-9]+|importmap" visor.html`. La plantilla ya resuelve todas.

## Extraer medidas del código viejo

- **Escala**: busca la unidad real. Un comentario como `150x150mm conceptualized as 6x6 units` indica 25 mm por unidad; `drumRadius = 20 // ~40cm` indica cm. Pásalo todo a mm.
- **Pivote**: Three centra las geometrías, así que `mesh.position.y = h / 2` significa base en el suelo. En el SPEC, `pos` es el centro de la base, entonces `y = 0`.
- **Ángulos**: `rotation` está en radianes y `rot` en grados (`Math.PI / 12` = 15°).
- **Textos**: leyendas, títulos y comentarios son afirmaciones, no medidas. Calcula lo derivado (volumen del cilindro, altura sumada de plataforma y maceta) y compáralo con lo que el texto dice y con los documentos del repo. Cada diferencia es una contradicción del inventario.
- **Contenido**: conserva piezas, capas, mensajes importantes (como `avisos`) y enlaces a documentos hermanos (como `enlaces`).

## Actualizar Three.js

La versión está en una sola línea: el `importmap` de `template.html`. Si la cambias, verifica `template.html` y revisa los avisos de deprecación que imprime `verify.mjs`.
