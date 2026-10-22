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

  /* --- Formulario: arma el mensaje y abre WhatsApp --- */
  var form = document.getElementById('contactForm');
  var errorBox = document.getElementById('formError');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var nombre = form.nombre.value.trim();
      var telefono = form.telefono.value.trim();
      var email = form.email.value.trim();
      var servicio = form.servicio.value;
      var mensaje = form.mensaje.value.trim();

      var faltan = [];
      if (!nombre) faltan.push(form.nombre);
      if (!telefono) faltan.push(form.telefono);

      form.nombre.removeAttribute('aria-invalid');
      form.telefono.removeAttribute('aria-invalid');

      if (faltan.length) {
        faltan.forEach(function (f) { f.setAttribute('aria-invalid', 'true'); });
        if (errorBox) {
          errorBox.textContent = 'Por favor complete su nombre y un teléfono de contacto.';
          errorBox.hidden = false;
        }
        faltan[0].focus();
        return;
      }

      if (errorBox) errorBox.hidden = true;

      var texto =
        'Hola JP Security SAS, quisiera solicitar un presupuesto.\n\n' +
        'Nombre: ' + nombre + '\n' +
        'Teléfono: ' + telefono + '\n' +
        (email ? 'Correo: ' + email + '\n' : '') +
        'Servicio de interés: ' + servicio + '\n' +
        (mensaje ? 'Detalle: ' + mensaje : '');

      window.open(
        'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(texto),
        '_blank',
        'noopener'
      );
    });
  }
})();
