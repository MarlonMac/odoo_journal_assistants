# Roadmap: Asistente de Compra de Activos

El desarrollo futuro de este módulo se centrará en integrarlo más profundamente con el ciclo de vida de los activos gestionados por el módulo `base_accounting_kit`.

## v1.1.0 (Planeado)

### Creación Automática del Activo

* **Descripción:** Después de que el asiento contable de la compra sea `Registrado`, añadir un botón o una acción automática que permita crear el registro del "Activo" correspondiente en el modelo de `base_accounting_kit`.
* **Beneficio:** Esto conectaría el flujo de compra con el flujo de gestión y depreciación de activos, eliminando la necesidad de crear el activo manualmente en otro menú y reduciendo la posibilidad de olvidos o errores.
* **Consideraciones Técnicas:**
  * Añadir un botón "Crear Activo" en el formulario, visible solo en el estado `posted`.
  * El botón llamará a una función que leerá los datos del asistente (nombre, categoría, monto, fecha) y los usará para crear un nuevo registro en el modelo de activos de Cybrosys (`account.asset.asset`).
  * Se creará un enlace (`Many2one`) desde el asistente al activo creado para mantener la trazabilidad.
