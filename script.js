/* JP Security SAS — interacciones de la landing */
(function () {
  'use strict';

  var WHATSAPP = '5492616962342';

  /* --- Año actual en el pie --- */
  var year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());

  /* --- Menú móvil --- */
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('nav');

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    });

    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        toggle.setAttribute('aria-label', 'Abrir menú');
      }
    });
  }

  /* --- Aparición progresiva de secciones --- */
  var targets = document.querySelectorAll(
    '.svc-card, .value-grid li, .obj-card, .team-card, .steps li, .form, .contact-list'
  );

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px' });

    targets.forEach(function (el) {
      el.classList.add('reveal');
      io.observe(el);
    });
  }

  /* --- Formulario de contacto --- */
  var form = document.getElementById('contactForm');
  var errorBox = document.getElementById('formError');
  var okBox = document.getElementById('formOk');
  var submitBtn = document.getElementById('formSubmit');

  function mostrar(caja, texto) {
    if (!caja) return;
    caja.textContent = texto;
    caja.hidden = false;
  }

  function ocultarMensajes() {
    if (errorBox) errorBox.hidden = true;
    if (okBox) okBox.hidden = true;
  }

  function armarTexto(d) {
    return 'Hola JP Security SAS, quisiera solicitar un presupuesto.\n\n' +
      'Nombre: ' + d.nombre + '\n' +
      'Teléfono: ' + d.telefono + '\n' +
      (d.email ? 'Correo: ' + d.email + '\n' : '') +
      'Servicio de interés: ' + d.servicio + '\n' +
      (d.mensaje ? 'Detalle: ' + d.mensaje : '');
  }

  /* Los enlaces de WhatsApp llevan la consulta ya escrita si la persona
     completó el formulario; si no, el saludo de siempre. Solo se abren
     cuando se hace clic. */
  function enlaceWhatsApp() {
    var texto = 'Hola JP Security SAS, quisiera solicitar un presupuesto.';

    if (form && form.nombre.value.trim() && form.telefono.value.trim()) {
      texto = armarTexto({
        nombre: form.nombre.value.trim(),
        telefono: form.telefono.value.trim(),
        email: form.email.value.trim(),
        servicio: form.servicio.value,
        mensaje: form.mensaje.value.trim()
      });
    }

    return 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(texto);
  }

  Array.prototype.forEach.call(
    document.querySelectorAll('a[href*="wa.me"]'),
    function (enlace) {
      enlace.addEventListener('click', function () {
        enlace.href = enlaceWhatsApp();
      });
    }
  );

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      ocultarMensajes();

      var datos = {
        nombre: form.nombre.value.trim(),
        telefono: form.telefono.value.trim(),
        email: form.email.value.trim(),
        servicio: form.servicio.value,
        mensaje: form.mensaje.value.trim()
      };

      var faltan = [];
      if (!datos.nombre) faltan.push(form.nombre);
      if (!datos.telefono) faltan.push(form.telefono);

      form.nombre.removeAttribute('aria-invalid');
      form.telefono.removeAttribute('aria-invalid');

      if (faltan.length) {
        faltan.forEach(function (f) { f.setAttribute('aria-invalid', 'true'); });
        mostrar(errorBox, 'Por favor complete su nombre y un teléfono de contacto.');
        faltan[0].focus();
        return;
      }

      var textoOriginal = submitBtn ? submitBtn.textContent : '';
      if (submitBtn) {
        submitBtn.setAttribute('aria-busy', 'true');
        submitBtn.textContent = 'Enviando…';
      }

      function restaurar() {
        if (submitBtn) {
          submitBtn.removeAttribute('aria-busy');
          submitBtn.textContent = textoOriginal;
        }
      }

      fetch('/api/contacto', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(datos)
      })
        .then(function (res) {
          return res.json().catch(function () { return {}; })
            .then(function (cuerpo) { return { ok: res.ok, cuerpo: cuerpo }; });
        })
        .then(function (r) {
          restaurar();
          if (r.ok && r.cuerpo.ok) {
            form.reset();
            mostrar(okBox, '¡Gracias! Recibimos su consulta y nos comunicamos a la brevedad.');
            return;
          }
          // El servidor rechazó la consulta y explicó por qué
          mostrar(errorBox, r.cuerpo.error ||
            'No pudimos enviar la consulta. Volvé a intentar o escribinos por WhatsApp.');
        })
        .catch(function () {
          mostrar(errorBox,
            'No pudimos conectar con el servidor. Volvé a intentar en unos minutos ' +
            'o escribinos por WhatsApp.');
          restaurar();
        });
    });
  }
})();
