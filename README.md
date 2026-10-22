# JP Security SAS — Landing page

Sitio institucional de **JP Security SAS**, empresa de seguridad física y electrónica
de la provincia de Mendoza, Argentina.

## Contenido

- **Hero** con identidad institucional (escudo) y llamados a la acción.
- **Servicios**: seguridad física (vigilancia, control de accesos, rondas, custodia,
  eventos) y seguridad electrónica (CCTV, alarmas, control de acceso, monitoreo,
  cercos eléctricos, mantenimiento).
- **Nosotros**: diferenciales de solidez y responsabilidad.
- **Objetivos en actividad**: Balbi, Barrio AMPROS, Clínica San Andrés.
- **Equipo**: presidencia, dirección técnica, asesoría/auditoría y supervisión.
- **Cómo trabajamos**: relevamiento, propuesta, implementación y auditoría.
- **Contacto**: formulario que arma el mensaje y lo envía por WhatsApp, más
  teléfono y correo directos.

## Estructura

```
index.html      Página completa
styles.css      Estilos (paleta institucional: azul noche, acero, rojo)
script.js       Menú móvil, animaciones de aparición y formulario → WhatsApp
assets/         Logo y favicons derivados del escudo institucional
```

Sitio estático, sin dependencias ni proceso de build.

## Ver en local

```bash
python3 -m http.server 8000
# abrir http://localhost:8000
```

## Publicar

Cualquier hosting estático sirve (GitHub Pages, Netlify, Vercel, Hostinger).
Para GitHub Pages: Settings → Pages → Branch, y elegir la rama que contiene estos archivos.

## Datos a revisar antes de publicar

- Teléfono: **261 696 2342** (el enlace de WhatsApp usa `5492616962342`).
- Correo: **Jpseguridadsas@gmail.com**.
- Si se incorpora dominio propio, actualizar las URLs absolutas de las etiquetas
  Open Graph en `index.html`.
