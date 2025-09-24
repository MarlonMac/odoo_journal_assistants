# ROADMAP: Ecosistema de Asistentes de Asientos Contables

Este documento describe la hoja de ruta para el desarrollo de los módulos que componen el ecosistema.

---

## Fase 1: Fundación y Primer Asistente (Refactorización) ✅

* **`journal_entry_assistant_base` (v1.0.0):** ✅
  * **Objetivo:** Crear el módulo base con un modelo abstracto que gestione estados (borrador, registrado, cancelado), la lógica de los botones, la secuencia de referencia y el chatter.
* **`expense_assistant` (v1.0.0):** ✅
  * **Objetivo:** Refactorizar el módulo `corporate_expense_manager` existente para que herede del nuevo módulo base.
  * **Funcionalidad:** Incluirá toda la funcionalidad que hemos desarrollado hasta la v1.4.0 (categorías, reembolsos, adjuntos requeridos, etc.).

---

## Fase 2: Expansión del Ecosistema

* **`asset_purchase_assistant` (v1.0.0):** ✅
  * **Objetivo:** Asistente para registrar la compra de activos fijos, generando el asiento contable inicial.
  * **Campos:** Nombre, Categoría de Activo, Proveedor, Monto, Cuenta de Activo Fijo.

* **`loan_payment_assistant` (v1.0.0):** ✅
  * **Objetivo:** Asistente para registrar pagos de préstamos, separando capital e intereses.
  * **Campos:** Préstamo, Monto Capital, Monto Intereses, Diario de Pago.

---

## Fase 3: Funcionalidades Avanzadas y de Control

* **Flujo de Aprobación (en `base` v1.0.0):** ✅
  * **Objetivo:** Añadir una capa de aprobación opcional al módulo base para que cualquier asistente pueda tener un flujo de "borrador -> para aprobar -> registrado".
* **`equity_movement_assistant` (v1.0.0):**
  * **Objetivo:** Asistente para registrar movimientos de patrimonio como dividendos o aportes.

---
