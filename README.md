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
.github/workflows/          Build, publicación de la imagen y deploy al VPS
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

## Despliegue con GitHub Actions

`.github/workflows/docker-publish.yml` hace todo en un solo push:

1. **Construye** la imagen.
2. **La prueba**: la levanta y verifica healthcheck, home, CSS, JS, logo y
   cabeceras de seguridad. Si algo falla, no publica ni despliega.
3. **Publica** en `ghcr.io/pel-matiasvaldivia/jpsecutirysas`
   (`linux/amd64` y `linux/arm64`).
4. **Despliega en el VPS** por SSH: copia `docker-compose.prod.yml`, hace
   `docker compose pull` + `up -d` y espera a que el contenedor quede sano.

En pull requests sólo construye y testea. El deploy corre en la rama por
defecto, en tags `v*` y a mano desde *Actions → Run workflow*.

El deploy usa el **digest** de la imagen, no `latest`: el VPS corre exactamente
el binario que pasó el smoke test, sin ambigüedad.

### Etiquetas de la imagen

| Evento | Tag |
|---|---|
| Push a la rama por defecto | `latest` y el nombre de la rama |
| Push a otra rama | nombre de la rama |
| Tag `v1.2.3` | `1.2.3`, `1.2` |
| Cualquier push | `sha-<commit>` |

### Preparar el VPS (una sola vez)

1. Instalar Docker con el plugin de Compose v2:

   ```bash
   curl -fsSL https://get.docker.com | sh
   docker compose version
   ```

2. Crear un usuario de deploy y su clave SSH (desde tu máquina):

   ```bash
   ssh-keygen -t ed25519 -f ~/.ssh/jpsecurity_deploy -C "github-actions"
   ssh-copy-id -i ~/.ssh/jpsecurity_deploy.pub usuario@IP_DEL_VPS
   ```

   El usuario tiene que poder correr `docker` (estar en el grupo `docker`).

3. Abrir el puerto 80 en el firewall:

   ```bash
   sudo ufw allow 80/tcp
   ```

4. Hacer **público** el paquete en GHCR, así el VPS puede descargarlo sin
   credenciales: pestaña **Packages** del repositorio → el paquete →
   *Package settings* → *Change visibility* → **Public**.

### Secrets y variables del repositorio

En *Settings → Secrets and variables → Actions*:

**Secrets** (obligatorios para que corra el deploy):

| Secret | Valor |
|---|---|
| `VPS_HOST` | IP o dominio del VPS |
| `VPS_USER` | Usuario SSH de deploy |
| `VPS_SSH_KEY` | Contenido de la clave **privada** (`~/.ssh/jpsecurity_deploy`, completa, incluidas las líneas `BEGIN`/`END`) |
| `VPS_KNOWN_HOSTS` | Opcional pero recomendado: salida de `ssh-keyscan IP_DEL_VPS`. Sin esto, el workflow confía en la clave que presente el servidor en cada corrida |

Si `VPS_HOST` no está cargado, el workflow construye y publica la imagen y
saltea el deploy sin fallar.

**Variables** (opcionales, con valor por defecto):

| Variable | Default | Para qué |
|---|---|---|
| `VPS_PATH` | `/opt/jpsecurity` | Dónde vive el stack en el servidor |
| `HTTP_PORT` | `80` | Puerto publicado en el VPS |
| `VPS_SSH_PORT` | `22` | Puerto SSH |

### Operar el stack a mano en el VPS

El workflow deja el `docker-compose.yml` y un `.env` con la imagen desplegada,
así que en el servidor funciona todo lo habitual:

```bash
cd /opt/jpsecurity
docker compose ps
docker compose logs -f
docker compose restart
```

Para volver a una versión anterior:

```bash
IMAGE=ghcr.io/pel-matiasvaldivia/jpsecutirysas:sha-abc1234 docker compose up -d
```

## Datos a revisar antes de publicar

- Teléfono: **261 696 2342** (el enlace de WhatsApp usa `5492616962342`).
- Correo: **Jpseguridadsas@gmail.com**.
- Si se incorpora dominio propio, actualizar las URLs absolutas de las etiquetas
  Open Graph en `index.html`.
