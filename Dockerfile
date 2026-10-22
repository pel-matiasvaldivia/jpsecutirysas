# JP Security SAS — sitio estático servido con nginx
FROM nginx:1.27-alpine

LABEL org.opencontainers.image.title="JP Security SAS" \
      org.opencontainers.image.description="Landing institucional de JP Security SAS (Mendoza, Argentina)" \
      org.opencontainers.image.source="https://github.com/pel-matiasvaldivia/jpsecutirysas" \
      org.opencontainers.image.licenses="UNLICENSED"

# Configuración propia: gzip, cacheo de assets, cabeceras de seguridad y /healthz
COPY docker/nginx.conf            /etc/nginx/conf.d/default.conf
COPY docker/security-headers.conf /etc/nginx/snippets/security-headers.conf

# Contenido del sitio
COPY index.html styles.css script.js /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

# Sella las URLs de styles.css y script.js con un hash de su contenido.
# El index.html nunca se cachea, así que cada visitante recibe el HTML nuevo;
# como apunta a una URL que ningún navegador tiene guardada, el CSS y el JS
# viejos quedan descartados al instante, sin esperar a que venza su caché.
RUN set -eu; \
    version="$(cat /usr/share/nginx/html/styles.css /usr/share/nginx/html/script.js \
               | sha256sum | cut -c1-10)"; \
    sed -i "s/__ASSET_VERSION__/$version/g" /usr/share/nginx/html/index.html; \
    if grep -q "__ASSET_VERSION__" /usr/share/nginx/html/index.html; then \
      echo "No se reemplazó la versión de los assets"; exit 1; \
    fi; \
    echo "Versión de assets: $version"

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1
