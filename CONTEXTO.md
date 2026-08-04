# CONTEXTO.md

## Qué es este proyecto

Sitio estático de "La Otra Carrera": un archivador de guías simples (`index.html`)
que enseña a usar IA para tareas cotidianas (comunicados del colegio, boletas,
reuniones, mensajes difíciles), más un quiz independiente de la tabla periódica
(`reto-tabla-periodica.html`, actualmente sin enlazar desde el sitio principal).

## Stack

HTML + CSS + JS vanilla, sin build ni dependencias. Todo el CSS y JS vive
inline dentro de cada archivo `.html`. Hosteado en GitHub Pages.

## Estructura

- `index.html` — sitio principal (guías).
- `reto-tabla-periodica.html` — quiz de química, página independiente.
- `images/` — `mascot-badge.png` (favicon/logo), `monito-footer.jpeg` (footer).

## Estado conocido / pendientes

- `reto-tabla-periodica.html` no está enlazada desde `index.html`.
- Los botones de Discord y Mastodon en el footer son placeholders (no funcionan).
- Dominio real de GitHub Pages sin confirmar (afecta las URLs de Open Graph).
- Ver informe de revisión de 2026-08-04 para el detalle completo de mejoras
  priorizadas (SEO, accesibilidad, rendimiento, duplicación de código).

## Convenciones

- Cada guía nueva en `index.html` sigue el mismo formato: 3 pasos, ejemplo
  de conversación (burbujas), callout "Lo importante", sugerencias extra.
- El quiz de tabla periódica es data-driven (array `ELEMENTS`); las guías
  del index, en cambio, están hardcodeadas a mano — ver informe para
  recomendación de unificar el patrón.
