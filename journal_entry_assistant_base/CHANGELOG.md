# Changelog

## [1.0.0] - 2025-09-26

### Added

- **Lanzamiento Inicial del Módulo Base.**
- **Modelo Abstracto `assistant.journal.entry.base`:** Proporciona la estructura de datos y lógica fundamental.
- **Flujo de Aprobación:** Implementación del flujo completo de estados, incluyendo `Para Aprobar` y `Aprobado`, con sus respectivos botones y lógica.
- **Grupo de Seguridad:** Creación del grupo `Aprobador de Asistentes de Diario` para controlar el acceso a las acciones de aprobación y registro.
- **Sistema de Pago Integrado:** Se añadió la lógica (`action_register_payment`) para llamar al asistente de pagos nativo de Odoo, junto con los campos para rastrear los saldos (`amount_paid`, `amount_due`).
- **Enlace con Asientos y Pagos:** Se extendieron los modelos `account.move` y `account.payment` para incluir una referencia al asistente que los originó.
