# Roadmap: Módulo Base de Asistentes

Este documento describe las futuras mejoras planeadas para el módulo base.

## v1.1.0 (Planeado)

### Flujo de Aprobación

* **Descripción:** Añadir una capa de aprobación opcional al flujo de estados. Esto permitirá que los asistentes que lo necesiten puedan implementar un proceso de validación por parte de un supervisor antes de que el asiento contable sea registrado.
* **Consideraciones Técnicas:**
  * Añadir nuevos estados al campo `state`, como `to_approve` (Para Aprobar) y `rejected` (Rechazado).
  * Implementar la lógica de los botones "Enviar para Aprobación", "Aprobar" y "Rechazar".
  * Introducir grupos de seguridad (`ir.rule`) para controlar qué usuarios tienen permiso para aprobar.
  