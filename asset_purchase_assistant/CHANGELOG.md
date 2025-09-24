# Changelog

## [1.0.0] - 2025-09-24

### Added

- **Lanzamiento Inicial del Asistente de Compra de Activos.**
- **Modelos Principales:** Creación de los modelos `asset.purchase.assistant` y `asset.category`.
- **Integración con el Ecosistema:** Herencia del módulo `journal_entry_assistant_base` para obtener el flujo de estados, la lógica de aprobación y la generación de asientos contables.
- **Flujo de Pago Dual:** Implementación de lógica para manejar tanto pagos directos como la creación de cuentas por pagar a proveedores.
- **Interfaz de Usuario Dinámica:** El formulario se adapta para mostrar los campos relevantes según el tipo de pago.
- **Dependencia de `base_accounting_kit`:** Asegura la compatibilidad con el entorno contable de Odoo Community.
