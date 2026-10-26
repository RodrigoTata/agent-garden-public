#!/usr/bin/env node
// armar.mjs — arma un gemelo digital desde su SPEC (<visor>.spec.js) y la plantilla, sin leer la plantilla.
// El .spec.js es la fuente; el .html es un producto que se regenera cada vez que cambia el SPEC.
//
// Uso:  node armar.mjs <visor.spec.js> [--out visor.html] [--reemplazar]
//       node armar.mjs --extraer <visor.html>      (saca el SPEC de un visor hecho con la plantilla a <visor>.spec.js)
//   El .spec.js contiene lo que va entre SPEC:INICIO y SPEC:FIN: constantes y `const SPEC = { … };`.
//   --reemplazar  permite pisar un .html que no salió de la plantilla (migración, ver MIGRAR.md).

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const flag = (name) => { const i = args.indexOf(name); return i >= 0 ? (args.splice(i, 1), true) : false; };
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const extraer = flag('--extraer'), reemplazar = flag('--reemplazar');
const outArg = opt('--out', null);
const file = args[0];
const uso = 'Uso: node armar.mjs <visor.spec.js> [--out visor.html] [--reemplazar]  |  node armar.mjs --extraer <visor.html>';
if (!file || !existsSync(file)) { console.error(uso); process.exit(2); }

// Devuelve [inicio, fin] del contenido entre el comentario SPEC:INICIO y el comentario SPEC:FIN, o null.
const INICIO = /\/\*\s*=+\s*SPEC:INICIO/, FIN = /\/\*\s*=+\s*SPEC:FIN/;
function bloque(html) {
  const ini = html.search(INICIO), fin = html.search(FIN);
  if (ini < 0 || fin < ini) return null;
  return [html.indexOf('*/', ini) + 2, fin];
}

if (extraer) {
  const html = readFileSync(file, 'utf8');
  const b = bloque(html);
  if (!b) { console.error('El visor no tiene los marcadores SPEC:INICIO / SPEC:FIN: no salió de la plantilla. Migra con MIGRAR.md.'); process.exit(2); }
  const dest = resolve(file).replace(/\.html?$/i, '') + '.spec.js';
  if (existsSync(dest)) { console.error(`Ya existe ${dest}: es la fuente, edítalo y vuelve a armar.`); process.exit(2); }
  writeFileSync(dest, html.slice(...b).trim() + '\n');
  console.log(`SPEC extraído: ${dest}`);
  process.exit(0);
}

const spec = readFileSync(file, 'utf8').trim();
if (!/\bconst\s+SPEC\s*=/.test(spec)) { console.error('El .spec.js debe declarar `const SPEC = { … };`.'); process.exit(2); }
if (INICIO.test(spec) || FIN.test(spec) || /<\/script/i.test(spec)) { console.error('El .spec.js no puede contener los comentarios marcadores SPEC:INICIO/SPEC:FIN ni </script>.'); process.exit(2); }

const plantilla = join(dirname(fileURLToPath(import.meta.url)), '..', 'template.html');
const base = readFileSync(plantilla, 'utf8');
const b = bloque(base);
if (!b) { console.error(`La plantilla ${plantilla} perdió sus marcadores SPEC.`); process.exit(2); }

const out = resolve(outArg ?? file.replace(/\.spec\.js$/i, '') + '.html');
if (out === resolve(file)) { console.error('Indica --out: el .html no puede pisar el .spec.js.'); process.exit(2); }
if (existsSync(out) && !reemplazar && !bloque(readFileSync(out, 'utf8'))) {
  console.error(`${out} existe y no salió de la plantilla. Extrae sus medidas (MIGRAR.md) y repite con --reemplazar.`); process.exit(2);
}
writeFileSync(out, base.slice(0, b[0]) + '\n\n' + spec + '\n\n' + base.slice(b[1]));
console.log(`visor: ${out}`);
