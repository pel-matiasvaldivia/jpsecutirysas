#!/bin/sh
# Completa el sitio con los datos de contacto antes de que arranque nginx.
#
# nginx ejecuta todo lo que haya en /docker-entrypoint.d/ al iniciar, así que
# esto corre en cada arranque del contenedor. El sitio original queda intacto
# en /usr/share/nginx/template y acá se genera una copia con los valores
# puestos: así, cambiar una variable y reiniciar alcanza para actualizarlo.
set -eu

PLANTILLA=/usr/share/nginx/template
DESTINO=/usr/share/nginx/html

# Valores por defecto: los de JP Security SAS
: "${CONTACT_PHONE_DISPLAY:=261 696 2342}"
: "${CONTACT_PHONE_LINK:=+542616962342}"
: "${CONTACT_WHATSAPP:=5492616962342}"

# wa.me solo acepta dígitos: nada de +, espacios ni guiones
CONTACT_WHATSAPP=$(printf '%s' "$CONTACT_WHATSAPP" | tr -cd '0-9')
if [ -z "$CONTACT_WHATSAPP" ]; then
    echo "configurar-sitio: CONTACT_WHATSAPP no tiene dígitos" >&2
    exit 1
fi

# Protege los caracteres que sed interpreta en el reemplazo
escapar() {
    printf '%s' "$1" | sed -e 's/[\\&|]/\\&/g'
}

cp "$PLANTILLA/index.html" "$PLANTILLA/styles.css" "$PLANTILLA/script.js" "$DESTINO/"

for archivo in index.html script.js; do
    sed -i \
        -e "s|__CONTACT_PHONE_DISPLAY__|$(escapar "$CONTACT_PHONE_DISPLAY")|g" \
        -e "s|__CONTACT_PHONE_LINK__|$(escapar "$CONTACT_PHONE_LINK")|g" \
        -e "s|__CONTACT_WHATSAPP__|$(escapar "$CONTACT_WHATSAPP")|g" \
        "$DESTINO/$archivo"
done

# El sello de versión se calcula acá, después de reemplazar: si cambia el
# número, cambia el contenido, y con él la URL que pide el navegador.
VERSION=$(cat "$DESTINO/styles.css" "$DESTINO/script.js" | sha256sum | cut -c1-10)
sed -i "s|__ASSET_VERSION__|$VERSION|g" "$DESTINO/index.html"

if grep -q "__CONTACT_\|__ASSET_VERSION__" "$DESTINO/index.html" "$DESTINO/script.js"; then
    echo "configurar-sitio: quedaron marcadores sin reemplazar" >&2
    exit 1
fi

echo "configurar-sitio: teléfono $CONTACT_PHONE_DISPLAY · WhatsApp $CONTACT_WHATSAPP · assets v$VERSION"
