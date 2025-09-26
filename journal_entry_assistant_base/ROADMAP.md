# Roadmap: Módulo Base de Asistentes

Este documento describe las futuras mejoras planeadas para el módulo base.

## v1.1.0 (Planeado)

### Motivo del Rechazo

* **Descripción:** Al hacer clic en el botón "Rechazar", en lugar de simplemente regresar el registro a "Borrador", se abrirá un `wizard` (ventana emergente) que pedirá al aprobador que escriba un motivo para el rechazo.
* **Beneficio:** Este motivo se registrará en el chatter del asistente, proporcionando una retroalimentación clara al usuario que creó el registro y mejorando la comunicación y la trazabilidad.
* **Consideraciones Técnicas:**
  * Crear un nuevo modelo `Transient` para el wizard con un campo de texto.
  * Sobrescribir el método `action_reject` para que abra una acción de ventana de este wizard.
  * El botón de confirmación del wizard escribirá el texto en el chatter (`message_post`) del asistente y luego cambiará su estado a `draft`.
