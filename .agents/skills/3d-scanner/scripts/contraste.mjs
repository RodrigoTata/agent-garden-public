#!/usr/bin/env node
// contraste.mjs — arma una variante temporal de un gemelo con la cámara de una foto y la verifica con verify.mjs
// de interactive-3d-structure. El visor original no se toca.
//
// Uso:  node contraste.mjs <visor.html> --camara x,y,z --nombre f1 [--sin-capa id[,id…]] [--out carpeta]
//   --camara    vector desde el objeto hacia la cámara de la foto (ejes del SPEC: +Y arriba, +Z frente, +X derecha)
//   --sin-capa  capas que la foto no muestra (p. ej. la tapa en una foto del interior)
// La variante va sin cotas, etiquetas ni objeto de escala. La captura a comparar es la de escritorio que imprime verify.

import { spawnSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, basename, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args.splice(i, 2)[1] : def; };
const camara = opt('--camara', null), nombre = opt('--nombre', 'foto'), sinCapa = opt('--sin-capa', '');
const outDir = resolve(opt('--out', join(tmpdir(), 'gemelo3d-contraste')));
const file = args[0];
const v = camara?.split(',').map(Number);
if (!file || !existsSync(file) || v?.length !== 3 || v.some((n) => !Number.isFinite(n))) {
  console.error('Uso: node contraste.mjs <visor.html> --camara x,y,z --nombre f1 [--sin-capa id,…] [--out carpeta]'); process.exit(2);
}

const verify = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'interactive-3d-structure', 'scripts', 'verify.mjs');
if (!existsSync(verify)) { console.error(`No encuentro verify.mjs en ${verify}: instala la skill interactive-3d-structure junto a esta.`); process.exit(2); }

const html = readFileSync(file, 'utf8');
const fin = html.indexOf('/* =============================== SPEC:FIN');
if (fin < 0) { console.error('El visor no tiene el marcador SPEC:FIN de la plantilla de interactive-3d-structure.'); process.exit(2); }
const capas = sinCapa.split(',').map((s) => s.trim()).filter(Boolean);
const ajuste = `/* contraste.mjs: variante temporal para comparar con la foto «${nombre}» */
SPEC.vistaInicial = ${JSON.stringify(v)}; SPEC.escala = 'ninguna'; SPEC.cotasGlobales = false; SPEC.cotas = []; SPEC.etiquetas = [];
SPEC.piezas = SPEC.piezas.filter((p) => !${JSON.stringify(capas)}.includes(p.capa));
`;
mkdirSync(outDir, { recursive: true });
const variante = join(outDir, `${basename(file, extname(file))}.contraste-${nombre}.html`);
writeFileSync(variante, html.slice(0, fin) + ajuste + html.slice(fin));
console.log(`variante: ${variante}`);
const r = spawnSync(process.execPath, [verify, variante, '--out', outDir], { stdio: 'inherit' });
process.exit(r.status ?? 1);
