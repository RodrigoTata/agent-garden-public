---
name: image-png-creator
description: Genera imágenes PNG con texto (folletos, infografías, afiches, fichas, posts, banners) componiéndolas en HTML con una ficha de fuentes y renderizándolas con un navegador sin ventana. Usar cuando el usuario pida una imagen, PNG, folleto, infografía o afiche con información, cuando una imagen existente traiga textos o datos erróneos, o cuando otra skill necesite entregar información como imagen.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Creador de imágenes PNG

Una imagen con texto se **compone**: los textos salen de la **ficha**, se diseñan en HTML con [plantilla.html](plantilla.html) y un navegador sin ventana los convierte en PNG. Un modelo generativo de imágenes no escribe ningún texto de la pieza. Ese modelo redacta de memoria: inventa sellos y certificaciones, junta rangos, agrega mecanismos y deja íconos vacíos. Además, como su PNG no tiene fuente, nadie puede auditarlo ni regenerarlo.

## La ficha

La ficha lista cada texto de la imagen con su fuente. Va en el comentario `FICHA` al inicio de la fuente HTML, para que la pieza se pueda auditar después.

| Fuente | Significa | Ejemplo |
|---|---|---|
| `doc` | Sale de un archivo, con su ubicación | `doc: docs/research.md §1.1` |
| `usuario` | Lo dijo el humano en esta conversación | `usuario` |
| `web` | Fuente primaria consultada | `web: https://…` |
| `agregado` | Redacción del agente sin fuente | `agregado` |

- `agregado` sirve para frases de orientación de sentido común ("cerrar bien la tapa"). Nunca para números, dosis, precios, fechas, plazos, efectos, mecanismos, nombres de organizaciones, sellos, certificaciones, registros, normas ni datos de contacto. Esos llevan `doc`, `usuario` o `web`, o no van en la pieza.
- Resumir está permitido. Cambiar una cifra, juntar dos rangos en uno o agregar una causa no lo está: "Arveja / Avellana (~1,0 g)" sobre una fuente que dice arveja 0,5–0,8 g y avellana 1,0–1,5 g es un error, no un resumen.
- Si dos fuentes chocan, gana la más primaria (la investigación o la decisión, no otra pieza derivada de ellas). El choque se informa en la entrega.
- Un dato sin fuente se busca: primero en el repo, después en documentos binarios con [context-extractor](../context-extractor/SKILL.md) y por último en la web con [research](../research/SKILL.md). Si no aparece, se pregunta al humano o sale de la pieza.

## Ramas

- **Crear** una pieza nueva: pasos 1 a 6.
- **Corregir** una imagen existente: los mismos pasos. En el paso 2 la ficha parte transcribiendo la imagen.
- Si se pide un documento navegable o de varias páginas, no una imagen, usa [generate-html-doc](../generate-html-doc/SKILL.md).

## Pasos

### 1. Encuadrar
Fija el formato con la tabla de [DISENO.md](DISENO.md), el público, el propósito y la lista de fuentes. Elige la paleta por dominio. Pregunta en un solo mensaje solo lo que no se pueda deducir de la conversación o del repo.

*Completo cuando*: el formato (ancho, alto o "libre" y escala), el público, la paleta y cada fuente a usar están nombrados.

### 2. Armar la ficha
**Crear**: lee cada fuente y escribe la ficha sección por sección, en el orden en que irán en la pieza.

**Corregir**: busca primero la fuente HTML de la imagen (mismo nombre, junto a ella). Si no existe, esa es la causa raíz: la imagen se redactó sin fuente. Lee la imagen por zonas con la lupa de 3d-scanner, de hasta 700 px de alto cada una, de arriba abajo:
```
node <carpeta de esta skill>/../3d-scanner/scripts/lupa.mjs <imagen> --zona x,y,ancho,alto
```
Transcribe cada texto tal cual. Después busca la fuente de cada uno y márcalo ✓ (coincide), ✗ (contradice, con el valor correcto) o ? (sin fuente). Revisa también lo que falta: datos que la fuente trae y la imagen omite, como contraindicaciones, vencimientos o advertencias.

*Completo cuando*: cada texto previsto tiene una fila con fuente y ningún `agregado` cae en lo prohibido. En **Corregir**, además, cada texto de la imagen original quedó marcado ✓, ✗ o ?.

### 3. Componer
Copia [plantilla.html](plantilla.html) junto al destino, con el nombre del PNG (`folleto.html` → `folleto.png`). Pega la ficha en su comentario `FICHA`, aplica la paleta y llena los bloques según [DISENO.md](DISENO.md). Borra los bloques que la pieza no usa.

*Completo cuando*: cada texto del HTML está en la ficha, y cada fila de la ficha está en el HTML o marcada `(fuera: motivo)`.

### 4. Renderizar
Si vas a reemplazar un PNG existente, respáldalo antes en el directorio temporal de la sesión.
```
node <carpeta de esta skill>/scripts/render.mjs <fuente.html> --ancho 1000 --escala 2 [--alto 1080] [--out imagen.png]
```
El script mide la altura del contenido, avisa con ⚠ si hay texto desbordado, piezas fuera del lienzo, imágenes rotas o contenido que no cabe en el alto fijo, y lista las líneas con números. Corrige cada ⚠ en el HTML y repite.

*Completo cuando*: el script imprime `VERDE`.

### 5. Cotejar
- Compara cada línea que el script lista bajo "líneas con números" con su fila de la ficha, cifra por cifra y unidad por unidad.
- Mira el PNG completo por zonas con la lupa, de arriba abajo, sin saltarte ninguna. Busca texto cortado o encimado, íconos vacíos, espacio muerto, bajo contraste y letra bajo el mínimo del formato.

*Completo cuando*: cada línea con números calza con la ficha y cada zona del PNG se miró en la lupa. Cualquier arreglo vuelve al paso 4.

### 6. Entregar
Informa:
- La ruta del PNG y la de su fuente HTML.
- Los textos `agregado`, para que el humano los apruebe o los saque.
- Los choques entre fuentes y cómo se resolvieron.
- En **Corregir**: la causa raíz, una tabla *Antes / Problema / Ahora* con cada ✗ y ?, y dónde quedó el respaldo del original. Nombra también otras piezas del repo que repitan los mismos errores.
