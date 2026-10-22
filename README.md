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

## Estructura del sitio

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
docker-compose.yml          Stack: levanta la imagen publicada en GHCR
.github/workflows/          Build y publicación de la imagen
```

## Levantar el stack

El `docker-compose.yml` no construye nada: baja la imagen que publicó GitHub
Actions en el registry del repositorio.

```bash
docker compose pull
docker compose up -d          # http://localhost
docker compose logs -f
docker compose down
```

Variables opcionales, por línea de comandos o en un archivo `.env` al lado del
compose:

| Variable | Default | Para qué |
|---|---|---|
| `IMAGE` | `ghcr.io/pel-matiasvaldivia/jpsecutirysas:latest` | Qué versión correr |
| `HTTP_PORT` | `80` | Puerto publicado en el host |

```bash
# Otro puerto
HTTP_PORT=8080 docker compose up -d

# Fijar una versión concreta en lugar de latest
IMAGE=ghcr.io/pel-matiasvaldivia/jpsecutirysas:sha-abc1234 docker compose up -d
```

Para que `docker compose pull` funcione sin credenciales, el paquete tiene que
ser público: pestaña **Packages** del repositorio → el paquete →
*Package settings* → *Change visibility* → **Public**. Si queda privado, hay
que hacer `docker login ghcr.io -u <usuario>` antes del pull.

## Trabajar sobre el sitio localmente

Sin Docker, que es lo más rápido para editar:

```bash
python3 -m http.server 8000      # http://localhost:8000
```

Y para probar la imagen con los cambios sin esperar al CI:

```bash
docker build -t jpsecurity:dev .
docker run --rm -p 8080:80 jpsecurity:dev
```

## Publicación de la imagen (GitHub Actions)

`.github/workflows/docker-publish.yml` corre en cada push:

1. **Construye** la imagen.
2. **La prueba**: la levanta y verifica healthcheck, home, CSS, JS, logo y
   cabeceras de seguridad. Si algo falla, no publica.
3. **Publica** en `ghcr.io/pel-matiasvaldivia/jpsecutirysas` para
   `linux/amd64` y `linux/arm64`.

En pull requests sólo construye y testea, no publica. No hace deploy a ningún
servidor: el despliegue se hace a mano con el `docker-compose.yml`.

### Etiquetas de la imagen

| Evento | Tag |
|---|---|
| Push a la rama por defecto | `latest` y el nombre de la rama |
| Push a otra rama | nombre de la rama |
| Tag `v1.2.3` | `1.2.3`, `1.2` |
| Cualquier push | `sha-<commit>` |

El resumen de cada corrida (*Actions* → la corrida → *Summary*) muestra las
etiquetas publicadas y el digest, útil para fijar una versión exacta en el
servidor.

## Datos a revisar antes de publicar

- Teléfono: **261 696 2342** (el enlace de WhatsApp usa `5492616962342`).
- Correo: **Jpseguridadsas@gmail.com**.
- Si se incorpora dominio propio, actualizar las URLs absolutas de las etiquetas
  Open Graph en `index.html`.
