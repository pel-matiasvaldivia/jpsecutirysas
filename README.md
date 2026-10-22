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
- **Contacto**: formulario que llega por correo y queda guardado en el
  servidor; WhatsApp y correo directos como alternativa, a un clic.

## Estructura del sitio

```
index.html      Página completa
styles.css      Estilos (paleta institucional: azul noche, acero, rojo)
script.js       Menú móvil, animaciones de aparición y envío del formulario
assets/         Logo y favicons derivados del escudo institucional
```

Sitio estático, sin dependencias ni proceso de build.

## Estructura del stack

```
Dockerfile                  Imagen nginx con el sitio
docker/nginx.conf           gzip, cacheo, /healthz, proxy a /api/ y try_files
docker/security-headers.conf Cabeceras de seguridad (incluidas en cada location)
docker/40-configurar-sitio.sh Completa teléfono y sello de versión al arrancar
api/server.py               Servicio de contacto (solo biblioteca estándar)
api/Dockerfile              Imagen del servicio de contacto
brochure/                   Brochure institucional en PDF y su fuente
docker-compose.yml          Stack: sitio + api, con las imágenes de GHCR
.env.example                Plantilla de configuración del correo
.github/workflows/          Build, test de integración y publicación
```

## Levantar el stack

El stack tiene dos servicios y no construye nada: baja las imágenes que publicó
GitHub Actions en el registry del repositorio.

| Servicio | Qué hace |
|---|---|
| `web` | nginx con el sitio. Publica el puerto 80 y pasa `/api/` a la api |
| `api` | Recibe el formulario, lo guarda y lo manda por correo. No se expone al exterior |

```bash
cp .env.example .env          # completar el correo (ver más abajo)
docker compose pull
docker compose up -d          # http://localhost
docker compose logs -f
docker compose down
```

Variables opcionales, por línea de comandos o en un archivo `.env` al lado del
compose:

| Variable | Default | Para qué |
|---|---|---|
| `IMAGE_WEB` | `ghcr.io/pel-matiasvaldivia/jpsecutirysas:latest` | Versión del sitio |
| `IMAGE_API` | `ghcr.io/pel-matiasvaldivia/jpsecutirysas/api:latest` | Versión de la api |
| `HTTP_PORT` | `80` | Puerto publicado en el host |

```bash
# Otro puerto
HTTP_PORT=8080 docker compose up -d

# Fijar una versión concreta en lugar de latest
IMAGE_WEB=ghcr.io/pel-matiasvaldivia/jpsecutirysas:sha-abc1234 docker compose up -d
```

Para que `docker compose pull` funcione sin credenciales, los dos paquetes
tienen que ser públicos: pestaña **Packages** del repositorio → cada paquete →
*Package settings* → *Change visibility* → **Public**. Si queda privado, hay
que hacer `docker login ghcr.io -u <usuario>` antes del pull.

## Trabajar sobre el sitio localmente

Sin Docker, que es lo más rápido para editar:

```bash
python3 -m http.server 8000      # http://localhost:8000
```

Y para probar la imagen con los cambios sin esperar al CI:

```bash
docker build -t jpsecurity-web:dev .
docker build -t jpsecurity-api:dev ./api
IMAGE_WEB=jpsecurity-web:dev IMAGE_API=jpsecurity-api:dev HTTP_PORT=8080 docker compose up -d
```

## Brochure en PDF

`brochure/JP-Security-SAS-Brochure.pdf` es el folleto de dos hojas A4 para
mandar por correo o WhatsApp, con el mismo contenido que la landing. Se genera
desde `brochure/brochure.html`; ver `brochure/README.md`.

## Cambiar el teléfono de contacto

El número no está fijo en la imagen: el contenedor completa el sitio al
arrancar con lo que diga el `.env`. En el `.env`, al lado del
`docker-compose.yml`:

```ini
CONTACT_PHONE_DISPLAY=261 696 2342      # como se ve en pantalla
CONTACT_PHONE_LINK=+542616962342        # enlace de llamada, formato internacional
CONTACT_WHATSAPP=5492616962342          # WhatsApp: solo dígitos, con el 9
```

Y se aplica con:

```bash
docker compose up -d
```

Son tres variables porque el mismo número se escribe distinto en cada lugar:
el visible lleva espacios, el de llamada lleva `+54` sin el 9, y el de WhatsApp
lleva el 9 de celular argentino y ningún signo.

Alcanza el `up -d`, sin `pull` ni imagen nueva: el sitio original viaja como
plantilla dentro de la imagen y se regenera en cada arranque. Por eso también
cambia el sello de los assets al cambiar el número, y los visitantes ven el
teléfono nuevo de inmediato.

El CI levanta el stack con un número de prueba y verifica que aparezca en la
página, en el enlace de llamada, en el de WhatsApp y en el JavaScript.

## Caché de los assets

`index.html` nunca se cachea, pero `styles.css` y `script.js` sí los guarda el
navegador. Para que un cambio llegue al visitante sin que tenga que vaciar nada:

- Las dos URLs llevan un sello con el hash de su contenido
  (`script.js?v=a1b2c3d4e5`), que el contenedor calcula al arrancar. Si el
  contenido cambia, cambia la URL, y el navegador la pide de nuevo porque es
  una dirección que nunca vio.
- Además se sirven con `Cache-Control: no-cache`, así se revalidan siempre.

Las dos cosas juntas por un motivo concreto: una versión anterior servía estos
archivos con `max-age` de 7 días, y mientras ese plazo no vence el navegador ni
siquiera consulta al servidor, de modo que un cambio de cabecera no alcanza para
desalojar lo que ya está guardado. El sello en la URL sí.

El CI verifica en cada push que el HTML servido traiga el sello reemplazado y
que los assets respondan con él.

## Formulario de contacto

Cuando alguien completa el formulario del sitio, el servicio `api`:

1. Valida los datos y limita las consultas por IP, para que un bot no inunde
   la casilla.
2. **Guarda la consulta** en `consultas.jsonl`, dentro del volumen `consultas`.
3. **Envía un correo** a `MAIL_TO` con los datos, poniendo como `Reply-To` el
   correo del interesado: responder desde Gmail le contesta directo a él.

Si el correo falla, la consulta igual queda guardada y el visitante ve el
mensaje de éxito. Si la api no responde, se le avisa en pantalla y se lo invita
a escribir por WhatsApp.

El formulario nunca abre WhatsApp por su cuenta. WhatsApp se abre solo al hacer
clic en el botón flotante o en los enlaces de la página; si en ese momento el
formulario ya tiene nombre y teléfono cargados, el chat se abre con la consulta
escrita, y si está vacío, con el saludo de siempre.

### Configurar el correo

En el `.env`, al lado del `docker-compose.yml`:

```ini
MAIL_TO=Jpseguridadsas@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USER=Jpseguridadsas@gmail.com
SMTP_PASSWORD=la-contraseña-de-aplicación
MAIL_FROM=Jpseguridadsas@gmail.com
```

Gmail no acepta la contraseña normal de la cuenta: hay que generar una
**contraseña de aplicación** (requiere verificación en 2 pasos activa) en
*myaccount.google.com → Seguridad → Contraseñas de aplicaciones*.

Después de cambiar el `.env`:

```bash
docker compose up -d
```

Sin SMTP configurado el formulario sigue funcionando: guarda todo en disco y lo
deja asentado en el log, pero no manda correo.

### Ver y respaldar las consultas

```bash
# Las últimas consultas, legibles
docker compose exec api cat /data/consultas.jsonl | tail -5

# Copia de respaldo al host
docker compose cp api:/data/consultas.jsonl ./consultas-backup.jsonl
```

El volumen `consultas` sobrevive a `docker compose down`. Para borrarlo también
hay que usar `docker compose down -v`.

### Ajustes opcionales del servicio

| Variable | Default | Para qué |
|---|---|---|
| `RATE_LIMIT_MAX` | `5` | Consultas aceptadas por IP en la ventana |
| `RATE_LIMIT_BURST` | `40` | Tope de peticiones por IP en la ventana |
| `RATE_LIMIT_WINDOW` | `600` | Ventana, en segundos |
| `MAX_BODY_BYTES` | `16384` | Tamaño máximo del formulario |

## Publicación de las imágenes (GitHub Actions)

`.github/workflows/docker-publish.yml` corre en cada push:

1. **Construye** las dos imágenes.
2. **Levanta el stack completo** con `docker compose` y lo prueba de punta a
   punta: healthcheck de ambos contenedores, home, CSS, JS, logo, cabeceras de
   seguridad, y el formulario contra la api real (consulta válida guardada en
   disco, consulta incompleta rechazada). Si algo falla,
   no publica.
3. **Publica** para `linux/amd64` y `linux/arm64`:
   - sitio: `ghcr.io/pel-matiasvaldivia/jpsecutirysas`
   - api: `ghcr.io/pel-matiasvaldivia/jpsecutirysas/api`

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
