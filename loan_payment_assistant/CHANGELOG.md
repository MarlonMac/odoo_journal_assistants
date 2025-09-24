# Changelog

## [1.0.0] - 2025-09-24

### Added

- **Lanzamiento Inicial del Asistente de Pago de Préstamos.**
- **Modelo `loan.payment.assistant`:** Creación del modelo principal que hereda de `journal_entry_assistant_base`.
- **Modelo `loan.loan`:** Creación de un modelo de configuración para registrar los préstamos y sus cuentas contables asociadas.
- **Lógica Contable Avanzada:** Implementación del método `_prepare_move_lines` para generar asientos de diario de 3 líneas (débito a capital, débito a intereses, crédito a banco/caja).
- **Campo de Monto Calculado:** El monto total del asistente es un campo computado a partir del capital y los intereses.
- **Vistas y Menús:** Creación de la interfaz de usuario para registrar pagos y para configurar los préstamos.
