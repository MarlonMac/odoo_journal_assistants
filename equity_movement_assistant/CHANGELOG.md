# Changelog

## [1.0.0] - 2025-09-26

### Added

- **Lanzamiento Inicial del Asistente de Movimientos de Patrimonio.**
- **Lógica de Declaración y Pago:** Se implementó el flujo contable de dos pasos. El asistente crea la declaración y la deuda (pasivo), y el pago se gestiona a través del botón "Registrar Pago".
- **Modelo `equity.movement.category`:** Permite la configuración detallada de los tipos de movimientos, incluyendo cuentas de patrimonio y pasivo.
- **Integración Completa con el Ecosistema:** Hereda el flujo de aprobación y el sistema de pagos del módulo base.
- **Seguridad Restringida:** El acceso está limitado a los grupos de Contabilidad y Administración.
