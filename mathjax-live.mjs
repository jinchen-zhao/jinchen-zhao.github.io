// Long-running MathJax renderer for editor.py: keeps MathJax loaded so each
// keystroke-save renders in milliseconds instead of starting Node again.
// Protocol: one JSON object per line on stdin, {"html": "..."}; replies with one
// line, {"html": "...", "css": "..."} or {"error": "..."}. Same TeX setup as
// mathjax.mjs, except that TeX errors render inline (half-typed math is normal
// while writing) instead of failing the build.

import {readFileSync} from 'node:fs';
import {createInterface} from 'node:readline';
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {CHTML} from 'mathjax-full/js/output/chtml.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {AllPackages} from 'mathjax-full/js/input/tex/AllPackages.js';

const {version} = JSON.parse(readFileSync(new URL('./node_modules/mathjax-full/package.json', import.meta.url), 'utf8'));
const FONTS = `https://cdn.jsdelivr.net/npm/mathjax-full@${version}/es5/output/chtml/fonts/woff-v2`;
const ENV = 'equation|align|gather|multline|flalign|alignat|eqnarray';
const nested = new RegExp(String.raw`\\\[\s*(\\begin\{(${ENV})\*?\}[\s\S]*?\\end\{\2\*?\})\s*\\\]`, 'g');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

createInterface({input: process.stdin}).on('line', (line) => {
  let out;
  try {
    const {html} = JSON.parse(line);
    const src = `<html><head></head><body><div id="live">${html.replace(nested, '$1')}</div></body></html>`;
    const output = new CHTML({fontURL: FONTS});
    const doc = mathjax.document(src, {
      InputJax: new TeX({packages: AllPackages, tags: 'ams', processEnvironments: true}),
      OutputJax: output,
    });
    doc.render();
    const live = adaptor.firstChild(adaptor.body(doc.document));
    out = {html: adaptor.innerHTML(live), css: adaptor.textContent(output.styleSheet(doc))};
  } catch (err) {
    out = {error: String(err && err.message || err)};
  }
  process.stdout.write(JSON.stringify(out) + '\n');
});
