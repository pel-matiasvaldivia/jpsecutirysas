# JP Security SAS — sitio estático servido con nginx
FROM nginx:1.27-alpine

LABEL org.opencontainers.image.title="JP Security SAS" \
      org.opencontainers.image.description="Landing institucional de JP Security SAS (Mendoza, Argentina)" \
      org.opencontainers.image.source="https://github.com/pel-matiasvaldivia/jpsecutirysas" \
      org.opencontainers.image.licenses="UNLICENSED"

# Configuración propia: gzip, cacheo de assets, cabeceras de seguridad y /healthz
COPY docker/nginx.conf            /etc/nginx/conf.d/default.conf
COPY docker/security-headers.conf /etc/nginx/snippets/security-headers.conf

# El sitio viaja como plantilla: los datos de contacto y el sello de versión
# los completa 40-configurar-sitio.sh en cada arranque del contenedor.
COPY index.html styles.css script.js /usr/share/nginx/template/
COPY assets/ /usr/share/nginx/html/assets/

COPY docker/40-configurar-sitio.sh /docker-entrypoint.d/40-configurar-sitio.sh
RUN chmod +x /docker-entrypoint.d/40-configurar-sitio.sh

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1
