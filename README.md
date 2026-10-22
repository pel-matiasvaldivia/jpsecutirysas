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

## Estructura del stack

```
Dockerfile                  Imagen nginx con el sitio
docker/nginx.conf           gzip, cacheo, /healthz y try_files
docker/security-headers.conf Cabeceras de seguridad (incluidas en cada location)
docker-compose.yml          Desarrollo: construye desde el código local
docker-compose.prod.yml     Producción: usa la imagen publicada en GHCR
.github/workflows/          Build + publicación de la imagen y deploy a Pages
```

## Ver en local

Sin Docker:

```bash
python3 -m http.server 8000      # http://localhost:8000
```

Con Docker:

```bash
docker compose up -d --build     # http://localhost:8080
docker compose logs -f web
docker compose down
```

El puerto se puede cambiar con `HTTP_PORT`:

```bash
HTTP_PORT=3000 docker compose up -d --build
```

## Despliegue con GitHub

### 1. Imagen de contenedor (GitHub Container Registry)

`.github/workflows/docker-publish.yml` corre en cada push:

1. Construye la imagen.
2. La levanta y hace un smoke test (healthcheck, home, assets y cabeceras).
3. Publica en `ghcr.io/pel-matiasvaldivia/jpsecutirysas` para `linux/amd64`
   y `linux/arm64`.

En los pull requests sólo construye y testea, no publica.

Etiquetas generadas:

| Evento | Tag |
|---|---|
| Push a la rama por defecto | `latest` y el nombre de la rama |
| Push a otra rama | nombre de la rama |
| Tag `v1.2.3` | `1.2.3`, `1.2` |
| Cualquier push | `sha-<commit>` |

Para levantarlo en un servidor:

```bash
docker login ghcr.io -u <usuario>            # si el paquete es privado
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Para fijar una versión concreta en lugar de `latest`:

```bash
IMAGE=ghcr.io/pel-matiasvaldivia/jpsecutirysas:1.2.3   docker compose -f docker-compose.prod.yml up -d
```

El paquete se publica privado por defecto. Para que `docker pull` funcione sin
credenciales: pestaña **Packages** del repositorio → el paquete →
*Package settings* → *Change visibility* → **Public**.

### 2. Sitio estático (GitHub Pages)

`.github/workflows/pages.yml` publica el sitio en Pages en cada push a la rama
por defecto. Requiere habilitarlo una vez:
**Settings → Pages → Source: GitHub Actions**.

Es la vía más rápida para tener el sitio online; la imagen de contenedor sirve
para alojarlo en un servidor propio o en cualquier hosting con Docker.

## Datos a revisar antes de publicar

- Teléfono: **261 696 2342** (el enlace de WhatsApp usa `5492616962342`).
- Correo: **Jpseguridadsas@gmail.com**.
- Si se incorpora dominio propio, actualizar las URLs absolutas de las etiquetas
  Open Graph en `index.html`.
