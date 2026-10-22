#!/usr/bin/env python3
"""Servicio de contacto de JP Security SAS.

Recibe el formulario del sitio, lo guarda en disco y lo reenvía por correo.
Usa solo la biblioteca estándar: no hay dependencias que actualizar.
"""

import json
import os
import re
import signal
import smtplib
import ssl
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs


def log(mensaje):
    ahora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{ahora}] {mensaje}", flush=True)


# --------------------------------------------------------------------------
# Configuración (todo por variables de entorno)
# --------------------------------------------------------------------------
def _int_env(nombre, por_defecto):
    try:
        return int(os.environ.get(nombre, "") or por_defecto)
    except ValueError:
        log(f"Valor inválido en {nombre}; se usa {por_defecto}")
        return por_defecto


PORT = _int_env("PORT", 8080)
DATA_FILE = os.environ.get("DATA_FILE", "/data/consultas.jsonl")

SMTP_HOST = os.environ.get("SMTP_HOST", "").strip()
SMTP_PORT = _int_env("SMTP_PORT", 587)
SMTP_USER = os.environ.get("SMTP_USER", "").strip()
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_SECURITY = os.environ.get("SMTP_SECURITY", "starttls").strip().lower()
SMTP_TIMEOUT = _int_env("SMTP_TIMEOUT", 15)

MAIL_TO = os.environ.get("MAIL_TO", "Jpseguridadsas@gmail.com").strip()
MAIL_FROM = os.environ.get("MAIL_FROM", "").strip() or SMTP_USER

# Dos topes por IP: uno alto para frenar bots, uno bajo para consultas
# aceptadas. Así corregir un dato del formulario no gasta cuota.
RATE_MAX = _int_env("RATE_LIMIT_MAX", 5)
RATE_BURST = _int_env("RATE_LIMIT_BURST", 40)
RATE_WINDOW = _int_env("RATE_LIMIT_WINDOW", 600)
MAX_BODY = _int_env("MAX_BODY_BYTES", 16 * 1024)

LIMITES = {
    "nombre": 120,
    "telefono": 40,
    "email": 180,
    "servicio": 120,
    "mensaje": 4000,
}

RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
RE_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


# --------------------------------------------------------------------------
# Límite de envíos por IP, para que un bot no inunde la casilla
# --------------------------------------------------------------------------
_cubetas = {"peticiones": defaultdict(deque), "consultas": defaultdict(deque)}
_candado = threading.Lock()


def permitido(ip, cubeta, tope):
    """Registra un intento y dice si la IP sigue dentro del tope."""
    ahora = time.monotonic()
    with _candado:
        registros = _cubetas[cubeta]
        marcas = registros[ip]
        while marcas and ahora - marcas[0] > RATE_WINDOW:
            marcas.popleft()
        if len(marcas) >= tope:
            return False
        marcas.append(ahora)

        # Evita que el diccionario crezca sin control
        if len(registros) > 2000:
            for clave in [k for k, v in registros.items() if not v]:
                del registros[clave]
        return True


# --------------------------------------------------------------------------
# Validación
# --------------------------------------------------------------------------
def limpiar(valor, maximo):
    if not isinstance(valor, str):
        valor = "" if valor is None else str(valor)
    valor = RE_CONTROL.sub("", valor.replace("\r\n", "\n")).strip()
    return valor[:maximo]


def validar(datos):
    """Devuelve (consulta, error). Si error no es None, se rechaza."""
    consulta = {campo: limpiar(datos.get(campo, ""), tope)
                for campo, tope in LIMITES.items()}

    if len(consulta["nombre"]) < 2:
        return None, "Indicá tu nombre."

    digitos = re.sub(r"\D", "", consulta["telefono"])
    if len(digitos) < 6:
        return None, "Indicá un teléfono de contacto válido."

    if consulta["email"] and not RE_EMAIL.match(consulta["email"]):
        return None, "El correo no parece válido."

    return consulta, None


# --------------------------------------------------------------------------
# Persistencia: cada consulta queda en disco aunque el correo falle
# --------------------------------------------------------------------------
_candado_archivo = threading.Lock()


def guardar(registro):
    try:
        carpeta = os.path.dirname(DATA_FILE)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        with _candado_archivo:
            with open(DATA_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(registro, ensure_ascii=False) + "\n")
        return True
    except OSError as exc:
        log(f"ERROR al guardar la consulta: {exc}")
        return False


# --------------------------------------------------------------------------
# Envío del correo
# --------------------------------------------------------------------------
def armar_mensaje(consulta, registro):
    cuerpo = (
        "Nueva consulta desde el sitio de JP Security SAS\n"
        "------------------------------------------------\n\n"
        f"Nombre:    {consulta['nombre']}\n"
        f"Teléfono:  {consulta['telefono']}\n"
        f"Correo:    {consulta['email'] or '(no indicó)'}\n"
        f"Servicio:  {consulta['servicio'] or '(no indicó)'}\n\n"
        "Mensaje:\n"
        f"{consulta['mensaje'] or '(sin detalle)'}\n\n"
        "------------------------------------------------\n"
        f"Recibida: {registro['fecha']}\n"
    )

    msg = EmailMessage()
    msg["Subject"] = f"Consulta web: {consulta['nombre']}"
    msg["From"] = formataddr(("Sitio JP Security SAS", MAIL_FROM))
    msg["To"] = MAIL_TO
    if consulta["email"]:
        # Así, responder desde Gmail le contesta directamente al interesado
        msg["Reply-To"] = formataddr((consulta["nombre"], consulta["email"]))
    msg.set_content(cuerpo)
    return msg


def enviar_correo(consulta, registro):
    if not (SMTP_HOST and MAIL_FROM and MAIL_TO):
        log("SMTP sin configurar: la consulta queda guardada, no se envía correo.")
        return False

    msg = armar_mensaje(consulta, registro)
    try:
        if SMTP_SECURITY == "ssl":
            contexto = ssl.create_default_context()
            servidor = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT,
                                        timeout=SMTP_TIMEOUT, context=contexto)
        else:
            servidor = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)

        with servidor:
            if SMTP_SECURITY == "starttls":
                servidor.starttls(context=ssl.create_default_context())
            if SMTP_USER:
                servidor.login(SMTP_USER, SMTP_PASSWORD)
            servidor.send_message(msg)

        log(f"Correo enviado a {MAIL_TO} (consulta de {consulta['nombre']})")
        return True
    except (smtplib.SMTPException, OSError, ssl.SSLError) as exc:
        log(f"ERROR al enviar el correo: {exc.__class__.__name__}: {exc}")
        return False


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    server_version = "jpsecurity-api"
    sys_version = ""
    protocol_version = "HTTP/1.1"

    def log_message(self, formato, *args):
        log(f"{self.client_ip()} {formato % args}")

    def client_ip(self):
        reenviado = self.headers.get("X-Forwarded-For", "")
        if reenviado:
            return reenviado.split(",")[0].strip()
        return self.client_address[0] if self.client_address else "-"

    def responder(self, codigo, payload):
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path.rstrip("/") in ("/api/healthz", "/healthz"):
            self.responder(200, {"ok": True})
        else:
            self.responder(404, {"ok": False, "error": "No encontrado"})

    def do_POST(self):
        if self.path.rstrip("/") not in ("/api/contacto", "/contacto"):
            self.responder(404, {"ok": False, "error": "No encontrado"})
            return

        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            largo = 0

        if largo <= 0 or largo > MAX_BODY:
            self.responder(413, {"ok": False, "error": "Mensaje demasiado largo."})
            return

        crudo = self.rfile.read(largo)
        tipo = (self.headers.get("Content-Type") or "").split(";")[0].strip()

        try:
            if tipo == "application/json":
                datos = json.loads(crudo.decode("utf-8"))
                if not isinstance(datos, dict):
                    raise ValueError("se esperaba un objeto JSON")
            else:
                datos = {k: v[0] for k, v in
                         parse_qs(crudo.decode("utf-8"), keep_blank_values=True).items()}
        except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
            self.responder(400, {"ok": False, "error": "No pudimos leer el formulario."})
            return

        if not permitido(self.client_ip(), "peticiones", RATE_BURST):
            self.responder(429, {"ok": False, "error": "Demasiadas peticiones."})
            return

        # Campo trampa: los visitantes no lo ven, los bots sí lo completan.
        # Se responde OK para no darles pistas.
        if limpiar(datos.get("sitio_web", ""), 50):
            log(f"Descartado por campo trampa ({self.client_ip()})")
            self.responder(200, {"ok": True})
            return

        consulta, error = validar(datos)
        if error:
            self.responder(400, {"ok": False, "error": error})
            return

        if not permitido(self.client_ip(), "consultas", RATE_MAX):
            self.responder(429, {
                "ok": False,
                "error": "Recibimos varias consultas desde tu conexión. "
                         "Probá de nuevo en unos minutos o escribinos por WhatsApp.",
            })
            return

        registro = {
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "ip": self.client_ip(),
            **consulta,
        }

        guardado = guardar(registro)
        enviado = enviar_correo(consulta, registro)

        if not guardado and not enviado:
            # No quedó registro en ningún lado: hay que avisarle al visitante.
            self.responder(503, {
                "ok": False,
                "error": "No pudimos registrar la consulta. "
                         "Escribinos por WhatsApp y la atendemos igual.",
            })
            return

        self.responder(200, {"ok": True, "email": enviado})


def main():
    servidor = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    servidor.daemon_threads = True

    def apagar(*_):
        log("Apagando…")
        threading.Thread(target=servidor.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, apagar)
    signal.signal(signal.SIGINT, apagar)

    log(f"Escuchando en :{PORT} · archivo: {DATA_FILE} · "
        f"correo: {'configurado -> ' + MAIL_TO if SMTP_HOST else 'SIN CONFIGURAR'}")
    try:
        servidor.serve_forever()
    finally:
        servidor.server_close()
        log("Detenido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
