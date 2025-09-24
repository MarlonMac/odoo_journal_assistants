# Roadmap: Asistente de Pago de Préstamos

El desarrollo futuro de este módulo se centrará en enriquecer la gestión y el seguimiento de los préstamos.

## v1.1.0 (Planeado)

### Seguimiento de Saldos del Préstamo

* **Descripción:** Mejorar el modelo `loan.loan` para incluir campos de "Monto Original" y "Saldo Pendiente". Cada vez que un pago sea `Registrado` a través del asistente, el saldo pendiente del préstamo asociado se actualizará automáticamente.
* **Beneficio:** Proporcionará una visión clara y en tiempo real del estado de cada deuda sin necesidad de generar reportes complejos, directamente desde la pantalla de configuración de préstamos.
* **Consideraciones Técnicas:**
  * Añadir los campos `original_amount` y `outstanding_balance` al modelo `loan.loan`.
  * Sobrescribir el método `action_post` en el modelo `loan.payment.assistant`. Después de llamar a `super()` para ejecutar la lógica base, se obtendrá el `principal_amount` y se restará del `outstanding_balance` del `loan_id` asociado.

## Mejoras Futuras

* **Tabla de Amortización:** Generar una tabla de amortización sugerida al crear un nuevo préstamo.
* **Reportes:** Crear reportes específicos sobre los intereses pagados por período o por acreedor.
