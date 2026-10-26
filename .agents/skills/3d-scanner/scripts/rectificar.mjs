#!/usr/bin/env node
// rectificar.mjs — convierte píxeles de una foto a mm sobre el plano de una cara de medidas conocidas (el ancla),
// corrigiendo la perspectiva con una homografía de 4 puntos.
//
// Uso:  node rectificar.mjs --esquinas "x,y x,y x,y x,y" --mm ANCHOxALTO [nombre=x,y ...] [nombre=x1,y1~x2,y2 ...]
//   --esquinas  sup-izq, sup-der, inf-der, inf-izq de la cara del ancla, en píxeles leídos con lupa.mjs
//   --mm        ancho × alto reales de esa cara, p. ej. 190x53
//   nombre=x,y          punto → mm (x desde el borde izquierdo, y desde el borde superior)
//   nombre=x1,y1~x2,y2  segmento → mm de cada extremo y largo
// Solo vale para puntos en el plano de esa cara.

const args = process.argv.slice(2);
const opt = (name) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : null; };
const esq = opt('--esquinas'), mm = opt('--mm');
if (!esq || !mm) { console.error('Uso: node rectificar.mjs --esquinas "x,y x,y x,y x,y" --mm ANCHOxALTO [nombre=x,y | nombre=x1,y1~x2,y2 ...]'); process.exit(2); }
const P = esq.trim().split(/\s+/).map((s) => s.split(',').map(Number));
const [A, B] = mm.toLowerCase().split('x').map(Number);
if (P.length !== 4 || P.some((p) => p.length !== 2 || p.some((v) => !Number.isFinite(v))) || !(A > 0 && B > 0)) {
  console.error('Esquinas: 4 puntos "x,y" (sup-izq sup-der inf-der inf-izq). --mm: ANCHOxALTO.'); process.exit(2);
}

function solve(M, b) {
  const n = b.length;
  for (let i = 0; i < n; i++) {
    let p = i; for (let r = i + 1; r < n; r++) if (Math.abs(M[r][i]) > Math.abs(M[p][i])) p = r;
    [M[i], M[p]] = [M[p], M[i]]; [b[i], b[p]] = [b[p], b[i]];
    for (let r = i + 1; r < n; r++) { const f = M[r][i] / M[i][i]; for (let c = i; c < n; c++) M[r][c] -= f * M[i][c]; b[r] -= f * b[i]; }
  }
  const x = Array(n);
  for (let i = n - 1; i >= 0; i--) { let s = b[i]; for (let c = i + 1; c < n; c++) s -= M[i][c] * x[c]; x[i] = s / M[i][i]; }
  return x;
}
const D = [[0, 0], [A, 0], [A, B], [0, B]];
const M = [], b = [];
P.forEach(([x, y], i) => {
  const [u, v] = D[i];
  M.push([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.push(u);
  M.push([0, 0, 0, x, y, 1, -v * x, -v * y]); b.push(v);
});
const h = solve(M, b);
if (h.some((v) => !Number.isFinite(v))) { console.error('Las esquinas no forman un cuadrilátero válido.'); process.exit(1); }
const map = ([x, y]) => { const w = h[6] * x + h[7] * y + 1; return [(h[0] * x + h[1] * y + h[2]) / w, (h[3] * x + h[4] * y + h[5]) / w]; };

// Control: razón alto/ancho en píxeles (lados opuestos promediados) frente a la real.
const d = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1]);
const ancho = (d(P[0], P[1]) + d(P[3], P[2])) / 2, alto = (d(P[0], P[3]) + d(P[1], P[2])) / 2;
const altoFoto = A * alto / ancho, desvio = (altoFoto / B - 1) * 100;
console.log(`control: alto según la foto ≈ ${altoFoto.toFixed(1)} mm vs ${B} mm real (${desvio >= 0 ? '+' : ''}${desvio.toFixed(1)} %)` +
  (Math.abs(desvio) > 5 ? '  ⚠ más de 5 %: revisa las esquinas o usa una foto más de frente' : '  ✓'));

const f = (v) => v.toFixed(1).padStart(7);
console.log(`${'nombre'.padEnd(22)}   x mm    y mm   largo mm`);
for (const a of args) {
  const [nombre, val] = a.split('=');
  if (!val) { console.error(`ignorado «${a}»: usa nombre=x,y o nombre=x1,y1~x2,y2`); continue; }
  const pts = val.split('~').map((s) => s.split(',').map(Number));
  if (pts.some((p) => p.length !== 2 || p.some((v) => !Number.isFinite(v)))) { console.error(`ignorado «${a}»: coordenadas inválidas`); continue; }
  const m = pts.map(map);
  if (m.length === 1) console.log(`${nombre.padEnd(22)} ${f(m[0][0])} ${f(m[0][1])}`);
  else console.log(`${nombre.padEnd(22)} ${f(m[0][0])} ${f(m[0][1])} → ${f(m[1][0]).trim()}, ${f(m[1][1]).trim()} ${f(d(m[0], m[1]))}`);
}
