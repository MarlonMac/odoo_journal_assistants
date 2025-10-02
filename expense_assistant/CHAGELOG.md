# Changelog

## [1.0.1] - 2025-10-02

- **[Multi-Empresa]** El modelo `expense.category` ahora es específico por compañía.
- **[Multi-Empresa]** Se han añadido reglas de seguridad y dominios para filtrar categorías, cuentas y diarios por la compañía activa, asegurando el correcto funcionamiento en entornos multi-empresa.

## [1.0.0] - 2025-09-23

### Added

- **Lanzamiento Inicial del Asistente de Gastos.**
- **Funcionalidad Completa:** Esta primera versión incluye todas las características del módulo `corporate_expense_manager` refactorizadas para la nueva arquitectura.
  - Gestión a través de **Categorías de Gastos**.
  - Doble flujo para **Pagos Directos** y **Cuentas por Pagar** (reembolsos).
  - Validación de **Adjunto Requerido**.
  - Campos para **Fecha de Vencimiento** y **Método de Pago Original**.
  - Asignación de **Empleados Responsables** (`hr` dependencia).
  - Integración con **Contabilidad Analítica**.
