# Brochure institucional

`brochure.html` es la fuente; el PDF se genera desde ahí, así no hay dos
versiones del contenido conviviendo.

```bash
npm install playwright          # solo la primera vez
node brochure/generar.mjs       # genera JP-Security-SAS-Brochure.pdf
```

Dos hojas A4, con el mismo contenido y la misma identidad que la landing:
servicios, diferenciales, objetivos en actividad, equipo, proceso de trabajo
y datos de contacto.

Los datos de contacto salen del entorno, igual que en el sitio:

| Variable | Default |
|---|---|
| `CONTACT_PHONE_DISPLAY` | `261 696 2342` |
| `CONTACT_EMAIL` | `Jpseguridadsas@gmail.com` |
| `CONTACT_WEB` | `jpsecuritysas.com.ar` |

```bash
CONTACT_PHONE_DISPLAY="261 570 8516" node brochure/generar.mjs
```

Para editarlo, abrí `brochure.html` en el navegador: se ve igual que el PDF.
Si agregás contenido, revisá que siga entrando en dos hojas — el generador no
lo recorta, simplemente saldría una tercera página.
