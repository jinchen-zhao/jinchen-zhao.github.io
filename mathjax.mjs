// Render TeX in built HTML pages to static CommonHTML, in place.
//   node mathjax.mjs _site/blog/post/index.html ...
// Pandoc (--mathjax) leaves math as <span class="math inline">\(..\)</span> and
// <span class="math display">\[..\]</span>. Equations are numbered per page
// (AMS style) so \label / \eqref work across the whole post.

import {readFileSync, writeFileSync} from 'node:fs';
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {CHTML} from 'mathjax-full/js/output/chtml.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import {AllPackages} from 'mathjax-full/js/input/tex/AllPackages.js';

const FONTS = 'https://cdn.jsdelivr.net/npm/mathjax-full@3.2.2/es5/output/chtml/fonts/woff-v2';
const ENV = 'equation|align|gather|multline|flalign|alignat|eqnarray';
// \[ \begin{align} .. \end{align} \] is a nesting error in MathJax: drop the outer \[ \].
const nested = new RegExp(String.raw`\\\[\s*(\\begin\{(${ENV})\*?\}[\s\S]*?\\end\{\2\*?\})\s*\\\]`, 'g');

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

let failed = false;
for (const file of process.argv.slice(2)) {
  const src = readFileSync(file, 'utf8').replace(nested, '$1');
  const doc = mathjax.document(src, {
    InputJax: new TeX({packages: AllPackages, tags: 'ams', processEnvironments: true,
                       formatError: (jax, err) => { throw err; }}),
    OutputJax: new CHTML({fontURL: FONTS}),
  });
  try {
    doc.render();
  } catch (err) {
    console.error(`${file}: TeX error: ${err.message}`);
    failed = true;
    continue;
  }
  writeFileSync(file, adaptor.doctype(doc.document) + '\n' + adaptor.outerHTML(adaptor.root(doc.document)));
}
process.exit(failed ? 1 : 0);
