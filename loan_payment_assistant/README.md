# Gestión de Préstamos y Pagos (Hub)

Este módulo es el corazón de la suite de "Gestión de Préstamos" dentro del ecosistema de Asistentes Contables. Transforma Odoo en un potente sistema para administrar deudas corporativas, centralizando contratos, desembolsos y amortizaciones.

**Versión:** 1.1.0
**Dependencias:** `journal_entry_assistant_base`, `expense_assistant`

---

## 📘 Documentación Funcional

### Visión General

El módulo permite gestionar el ciclo de vida completo de un préstamo, desde la firma del contrato hasta su pago total, pasando por la recepción de fondos.

### Características Principales

1. **Dashboard de Préstamos (Kanban):**
    * Visualización moderna de todos los contratos activos.
    * **Barra de Progreso:** Indica visualmente qué porcentaje de la deuda ha sido pagada.
    * **Alertas de Vencimiento:** Muestra cuántos días faltan para el próximo vencimiento.
    * **Organización por Estado:** Borrador, Activo, Pagado.

2. **Gestión de Contratos de Préstamos (El Hub):**
    * Registro centralizado de condiciones: Acreedor, Monto Original, Tasas, Cuentas Contables.
    * **Navegación 360°:** Botones inteligentes para ver todos los pagos y el desembolso original desde el mismo contrato.
    * **Acciones Directas:** Botones para "Registrar Desembolso" y "Registrar Pago" directamente desde la ficha del préstamo.

3. **Lógica de Pagos Inteligente:**
    * **Separación Capital/Interés:** Permite imputar el pago correctamente: el Capital reduce el saldo, el Interés se va al gasto.
    * **Cálculo Automático:** El saldo pendiente se actualiza en tiempo real con cada pago confirmado.
    * **Validaciones:** Impide pagar más capital del que se debe.

4. **Automatización y Ludificación:**
    * **Transición Automática:** Cuando el saldo llega a 0.00, el préstamo pasa automáticamente a estado **"Pagado"**.
    * **Efecto Rainbow Man:** ¡Celebración visual al completar una deuda!
    * **Reversión Segura:** Si cancelas un pago, el sistema devuelve el monto al saldo y reactiva el préstamo si es necesario.

### Flujo de Uso

1. **Creación del Contrato:**
    * Ir a *Asistentes de Diario > Gestión de Préstamos > Préstamos (Dashboard)*.
    * Crear nuevo. Definir Acreedor, Monto y Cuentas Contables.
    * *(Estado: Borrador)*.

2. **Recepción de Fondos (Recepción):**
    * Desde el contrato, clic en **"Registrar Recepción"**.
    * Confirmar la fecha, el diario de entrada (Banco) y adjuntar comprobante.
    * Al confirmar, el contrato pasa a **"Activo"** y se fija la fecha de inicio.

3. **Registro de Pagos (Amortización):**
    * Desde el contrato activo, clic en **"Registrar Pago de Cuota"**.
    * Indicar cuánto es Capital y cuánto Interés.
    * Al confirmar, se genera el asiento contable y se reduce el saldo.

---

## 🛠️ Documentación Técnica

### Arquitectura de Modelos

* **`loan.loan` (Modelo Maestro):**
  * Actúa como el "Hub". Contiene la verdad única sobre el saldo (`outstanding_balance`) y el estado del contrato.
  * Utiliza herencia de clase (`_inherit`) para integrar funcionalidades de mensajería (`mail.thread`) y lógica de otros módulos como `loan_reception_assistant`.
  * **Clave:** El campo `outstanding_balance` es `store=True` pero se actualiza mediante triggers en los métodos `action_post` y `action_cancel` de los asistentes hijos.

* **`loan.payment.assistant` (Modelo Transaccional):**
  * Hereda de `assistant.journal.entry.base`.
  * **Lógica de Asiento:** Genera asientos de 3 líneas (Débito Pasivo, Débito Gasto, Crédito Banco).
  * **Trigger:** Sobrescribe `action_post` para restar capital y `action_cancel` para sumar capital al `loan.loan`.

### Seguridad y Restricciones

* **Bloqueo de Edición:** Los campos estructurales del contrato (`original_amount`, `partner_id`, cuentas) están bloqueados contra escritura (`write`) cuando el estado es `active` o `paid`.
* **Integridad Multi-empresa:** Reglas de registro (`ir.rule`) implementadas para aislar préstamos por `company_id`.
* **Kanban Restringido:** Se ha deshabilitado `records_draggable`, `quick_create` y `group_create` para forzar el flujo de negocio estricto mediante botones.

### Extensiones (Hooks)

Este módulo está diseñado para ser extendido.

* **Recepción:** El módulo `loan_reception_assistant` extiende la vista del formulario para inyectar el botón de desembolso.
* **Cálculo de Fechas:** El método `_onchange_payment_term` utiliza la API nativa de plazos de pago de Odoo para calcular vencimientos.

---

**Desarrollado para:** Ecosistema de Asistentes Odoo 16 Community.
