# SPEC — esquema del gemelo digital

Referencia del bloque `SPEC:INICIO … SPEC:FIN` de [template.html](template.html). El motor valida todo lo de aquí: un campo mal escrito aparece como error rojo en el panel y en `verify.mjs`.

## Convenciones

- **Unidades**: mm en todo. Ángulos (`rot`, `giro`) en grados.
- **Ejes**: Y hacia arriba y suelo en `y = 0`. **+Z es el frente** (lo que ve la vista Frente) y **+X es la derecha** de quien mira el frente. Conviene poner el origen en el centro de la huella del conjunto.
- **`pos` = centro de la base** (el punto de apoyo) en `caja`, `caja-abierta`, `cilindro`, `esfera` y `panel` con `dims`. Para apilar, `y` = altura de lo que hay debajo. Las piezas definidas por puntos (`desde/hasta`, `puntos`, `esquinas`, `contorno`) usan coordenadas del padre, y ahí `pos` solo las desplaza.
- **El SPEC es JavaScript**: admite constantes, `map` y template literals. Ayudas disponibles: `fmtLen(mm)` → `"150 mm"` / `"2.25 m"`, `fmtNum(n)` y `litros(diam, alto, diamSup?)`.
- **Fuente única**: todo número que aparece en un texto (`nombre`, `nota`, `avisos`, `cotas[].texto`) se interpola desde una constante.

## Raíz

| Campo | Valor | Notas |
|---|---|---|
| `titulo` * | texto | Barra superior, `<title>` y nombre del PNG. |
| `subtitulo` | texto | |
| `capas` * | `[{ id, nombre, color? }]` | Una casilla por capa. Sin `color`, se usa el de su primera pieza. |
| `piezas` * | lista | Ver abajo. |
| `orientacion` | `{ modo: 'relativa' }` o `{ modo: 'cardinal', frente: 'S' }` | `frente` es hacia dónde mira +Z (N, NE, E, SE, S, SO, O, NO). |
| `escala` | `'auto'` · `'humano'` · `'tarjeta'` · `'ninguna'` | `auto` = persona de 1.75 m si el conjunto mide ≥ 600 mm; si no, tarjeta de 85.6 × 54 mm. |
| `vistaInicial` | `iso` · `frente` · `atras` · `izq` · `der` · `planta` · `[x, y, z]` | Por defecto `iso` (desde frente-derecha-arriba). Un vector elige otra dirección, p. ej. `[-1, 0.9, 1.25]` para ver desde frente-izquierda. |
| `explosionInicial` | 0–1 | Explosión con que abre el visor. Úsala cuando una tapa esconde el interior. |
| `cotasGlobales` | `true` · `false` · `{ capa }` | Ancho, fondo y alto automáticos. Usa `{ capa }` cuando antenas o mangueras agrandan la envolvente. |
| `cotas` | `[{ de, a, texto?, desplazar? }]` | Sin `texto`, rotula la distancia medida. `desplazar` separa la línea del objeto. |
| `etiquetas` | `[{ texto, en: [x,y,z], capa? }]` | Rótulo flotante (p. ej. «Opción A»). Con `capa` se enciende y apaga junto con ella; sin `capa`, va con las cotas. |
| `avisos` | `[{ nivel, titulo, texto }]` | `nivel`: `info` · `ok` · `alerta`. Para reglas de diseño y supuestos importantes. |
| `enlaces` | `[{ texto, href, icono? }]` | Botones en la barra hacia documentos hermanos (manual, BOM). |
| `materiales` | `{ clave: {...} }` | Agrega materiales o modifica presets (ver Materiales). |
| `constructores` | `{ nombre(THREE, p, ctx) }` | Formas a medida (ver Constructores). |

## Pieza — campos comunes

| Campo | Notas |
|---|---|
| `tipo` * | Uno de la tabla de tipos o el nombre de un constructor. |
| `nombre` * | Aparece en la ficha y en la lista de piezas. En `hijos` es opcional: un hijo sin nombre es parte de su grupo. |
| `capa` * | `id` de una capa. Los hijos heredan la del grupo. |
| `id` | Obligatorio si otra pieza lo usa en `dentroDe`. |
| `material` | Clave de material, por defecto `plastico-gris`. Los hijos heredan la del grupo. |
| `pos`, `rot` | `[x, y, z]` en mm y `[x, y, z]` en grados. |
| `nota` | Texto libre en la ficha: fuente, `supuesto`, código de compra. |
| `dentroDe` | `id` del contenedor. En `caja-abierta` se compara con el interior, en `cilindro` con el radio y el alto, y en los demás con la caja envolvente. Si no cabe, es error. |
| `explota` | `[dx, dy, dz]`: desplazamiento con el control de vista explosionada al 100 %. |
| `orden` | Orden de dibujo de translúcidos anidados: la pieza interior lleva el número menor (agua 1, estanque 2). |

## Tipos

| `tipo` | Campos | Uso típico |
|---|---|---|
| `caja` | `dims: [ancho X, alto Y, fondo Z]` | PCB, módulo, tapa, bloque |
| `caja-abierta` | `dims`, `pared` (3), `sinFondo` | Gabinete, cajón, jardinera, estanque rectangular |
| `cilindro` | `diam`, `alto`, `diamSup` (tronco de cono), `segmentos` | Estanque, maceta, bobina, poste vertical |
| `esfera` | `diam` | Marcador, LED, perilla |
| `barra` | `desde`, `hasta`, `diam`, `diamSup` | Tubo o poste en cualquier dirección, antena, eje |
| `viga` | `desde`, `hasta`, `seccion: [ancho, alto]`, `giro` | Madero, perfil, costanera, tornapunta |
| `manguera` | `puntos: [[x,y,z], …]` (2+), `diam` | Manguera, cable, pigtail. La ficha informa el largo real (sirve para cortar). |
| `panel` | `dims: [ancho, alto]` (plano vertical que mira a +Z) o `esquinas: [4 puntos]` | Malla, lona, pantalla, techo inclinado |
| `extrusion` | `contorno: [[x,y], …]` (plano XY), `profundidad` (hacia +Z) | Escuadra L, perfil, placa con forma |
| `grupo` | `hijos: [...]` en coordenadas del grupo | Subconjunto que se repite o se mueve junto |

Sección de `viga`: en piezas no verticales `alto` es la medida vertical; en verticales `ancho` va en X y `alto` en Z. `giro` rota la sección sobre el eje de la pieza.

## Repetición

- `en: [[x,y,z], …]`: una copia por posición (reemplaza `pos`).
- `repetir: { n, paso: [dx,dy,dz] }`: `n` copias desde `pos`. Sin `paso`, todas en el mismo lugar, lo que sirve con campos-función.
- En piezas repetidas **cualquier campo puede ser función** `(i) => valor`, con `i` desde 0. Así se definen los `puntos` de cada manguera o un `dentroDe` por copia.
- Las copias se llaman `Nombre 1…n` y sus ids `id-1…n`.

## Materiales

Presets: `madera`, `madera-oscura`, `metal`, `aluminio`, `laton` · `plastico-gris`, `plastico-negro`, `plastico-blanco`, `petg-verde`, `petg-azul`, `tpu-blanco`, `hdpe-azul`, `hdpe-translucido` · `pcb-verde`, `pcb-azul`, `pcb-negro`, `rele`, `bornera`, `componente`, `cable`, `pantalla`, `led-verde`, `led-rojo` · `manguera`, `agua`, `malla`, `malla-sombra`, `sustrato`, `follaje`, `tallo`, `goma`, `concreto`, `alerta`, `referencia`.

```js
materiales: {
  'petg-verde': { color: '#0f9f6e' },                       // modifica un preset
  'caja-ip65': { nombre: 'ABS gris IP65', color: '#9aa1a9', rugosidad: 0.55 },
  // otros campos: opacidad (0–1), metal (0–1), emisivo ('#hex'), emisivoIntensidad, doble (dos caras), bordes (aristas marcadas)
},
```

## Constructores

Sirven para formas que los tipos no arman (planta, pieza orgánica). Reciben la pieza en mm, devuelven un `THREE.Object3D` con pivote en el centro de la base y se usan con `tipo: '<nombre>'`.

```js
constructores: {
  planta(THREE, p, ctx) {
    const g = new THREE.Group();
    g.add(ctx.mesh(new THREE.CylinderGeometry(4, 6, 180, 8).translate(0, 90, 0), 'tallo'));
    g.add(ctx.mesh(new THREE.IcosahedronGeometry(90, 1).translate(0, 240, 0), 'follaje'));
    return g;
  },
},
```

Crea las mallas con `ctx.mesh(geometría, claveMaterial)` para que participen en sombras, rayos X y la ficha.

## Fragmentos por dominio

**Estructura de madera (cubicación).** La pendiente del techo sale sola de `desde/hasta`:
```js
const A = { ancho: 3000, fondo: 2000, altoFrente: 2000, altoAtras: 2250 };
const S2x4 = [41, 90];
orientacion: { modo: 'cardinal', frente: 'S' },
{ tipo: 'viga', nombre: 'Pilar frontal', capa: 'madera', material: 'madera', seccion: S2x4,
  en: [[-A.ancho / 2, 0, A.fondo / 2], [A.ancho / 2, 0, A.fondo / 2]], desde: [0, 0, 0], hasta: [0, A.altoFrente, 0] },
{ tipo: 'viga', nombre: 'Viga de techo', capa: 'madera', material: 'madera', seccion: S2x4,
  repetir: { n: 4, paso: [A.ancho / 3, 0, 0] }, pos: [-A.ancho / 2, 0, 0],
  desde: [0, A.altoAtras, -A.fondo / 2], hasta: [0, A.altoFrente, A.fondo / 2] },
{ tipo: 'panel', nombre: 'Malla sombra techo', capa: 'mallas', material: 'malla-sombra',
  esquinas: [[-A.ancho / 2, A.altoAtras, -A.fondo / 2], [A.ancho / 2, A.altoAtras, -A.fondo / 2],
             [A.ancho / 2, A.altoFrente, A.fondo / 2], [-A.ancho / 2, A.altoFrente, A.fondo / 2]] },
```

**Gabinete electrónico.** La tapa se levanta con la vista explosionada y el módulo se valida contra el interior:
```js
const CAJA = { lado: 150, alto: 70, tapa: 8, pared: 3 };
{ tipo: 'caja-abierta', id: 'caja', nombre: 'Caja IP65', capa: 'gabinete', dims: [CAJA.lado, CAJA.alto - CAJA.tapa, CAJA.lado], pared: CAJA.pared },
{ tipo: 'caja', nombre: 'Tapa', capa: 'gabinete', dims: [CAJA.lado, CAJA.tapa, CAJA.lado], pos: [0, CAJA.alto - CAJA.tapa, 0], explota: [0, 120, 0] },
{ tipo: 'grupo', nombre: 'Módulo 8 relés', capa: 'potencia', material: 'pcb-azul', pos: [0, CAJA.pared + 5, -40], dentroDe: 'caja',
  hijos: [{ tipo: 'caja', dims: [138, 1.6, 56] },
          { tipo: 'caja', nombre: 'Relé', material: 'rele', dims: [15.5, 15.5, 19], pos: [-57.75, 1.6, 8], repetir: { n: 8, paso: [16.5, 0, 0] } }] },
```

**Montaje hidráulico.** Las mangueras van con puntos por copia y el volumen se calcula a partir de la geometría:
```js
const T = { x: -450, diam: 320, alto: 450, agua: 400 };
const MACETAS = [[250, -400], [650, -400], /* … */];
{ tipo: 'cilindro', id: 'estanque', nombre: 'Estanque', capa: 'agua', material: 'hdpe-translucido', diam: T.diam, alto: T.alto, pos: [T.x, 0, 0], orden: 2 },
{ tipo: 'cilindro', nombre: 'Agua', capa: 'agua', material: 'agua', orden: 1, diam: T.diam - 10, alto: T.agua, pos: [T.x, 5, 0],
  nota: `≈ ${fmtNum(litros(T.diam - 10, T.agua))} L a ${fmtLen(T.agua)}` },
{ tipo: 'manguera', nombre: 'Línea', capa: 'riego', material: 'manguera', diam: 8, repetir: { n: MACETAS.length },
  puntos: (i) => [[T.x, 40, 0], [T.x, T.alto + 40, 0], [MACETAS[i][0], 900, MACETAS[i][1]]] },
```
