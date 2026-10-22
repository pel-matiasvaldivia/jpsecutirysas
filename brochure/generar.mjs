/**
 * Genera el brochure en PDF a partir de brochure.html.
 *
 *   node brochure/generar.mjs
 *
 * Los datos de contacto salen del entorno, igual que en el sitio:
 *   CONTACT_PHONE_DISPLAY, CONTACT_EMAIL, CONTACT_WEB
 */
import { chromium } from 'playwright';
import { readFile, writeFile, unlink } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AQUI = dirname(fileURLToPath(import.meta.url));

const DATOS = {
  __CONTACT_PHONE_DISPLAY__: process.env.CONTACT_PHONE_DISPLAY || '261 696 2342',
  __CONTACT_EMAIL__: process.env.CONTACT_EMAIL || 'Jpseguridadsas@gmail.com',
  __CONTACT_WEB__: process.env.CONTACT_WEB || 'jpsecuritysas.com.ar'
};

const SALIDA = join(AQUI, 'JP-Security-SAS-Brochure.pdf');

// El HTML se completa en una copia temporal, para no tocar la plantilla
const plantilla = await readFile(join(AQUI, 'brochure.html'), 'utf8');
let html = plantilla;
for (const [marca, valor] of Object.entries(DATOS)) {
  html = html.replaceAll(marca, valor);
}

const quedan = html.match(/__[A-Z_]+__/g);
if (quedan) throw new Error(`Marcadores sin reemplazar: ${[...new Set(quedan)].join(', ')}`);

const temporal = join(AQUI, '.brochure-generado.html');
await writeFile(temporal, html, 'utf8');

try {
  const navegador = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined
  });
  const pagina = await navegador.newPage();

  await pagina.goto(pathToFileURL(temporal).href, { waitUntil: 'networkidle' });
  await pagina.evaluate(() => document.fonts.ready);

  await pagina.pdf({
    path: SALIDA,
    format: 'A4',
    printBackground: true,
    margin: { top: '0', right: '0', bottom: '0', left: '0' }
  });

  await navegador.close();
  console.log(`Brochure generado: ${SALIDA}`);
} finally {
  await unlink(temporal).catch(() => {});
}
