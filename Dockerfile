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

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/healthz || exit 1
