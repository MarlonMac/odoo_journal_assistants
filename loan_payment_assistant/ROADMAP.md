# Roadmap: Gestión de Préstamos

Este documento rastrea la evolución de la suite de gestión de préstamos (`loan_payment_assistant` y sus módulos satélite).

## Historial de Versiones

### v1.1.0 (Lanzamiento Actual - Completado) ✅

Esta versión transformó los asistentes aislados en una suite integral de gestión.

* **Hub Centralizado:** El modelo `loan.loan` ahora actúa como el centro de mando.
* **Ciclo de Vida Completo:** Flujo estricto de `Borrador` > `Activo` (tras Recepción) > `Pagado`.
* **Dashboard Kanban:** Vista de tarjetas con barras de progreso visual y alertas de vencimiento.
* **Integridad de Datos:**
  * Seguimiento en tiempo real del `Saldo Pendiente`.
  * Lógica de reversión: Cancelar un pago restaura el saldo de la deuda.
  * Protección contra borrado de préstamos con movimientos.
  * **Soporte Multi-moneda:** Recepción estricta en moneda del contrato y Pagos flexibles en múltiples divisas con conversión automática.
* **Navegación 360°:** Botones para registrar desembolsos y pagos directamente desde el contrato.
* **Automatización:** Transición automática a "Pagado" y gamificación (Rainbow Man).

---

## v1.2.0 (Planeado) 🛠️

### 1. Modelo de Plan de Pagos (Amortización)

* **Objetivo:** Flexibilidad total en la definición de cuotas, superando las limitaciones de los plazos de pago estándar.
* **Implementación:** * Nuevo modelo vinculado al préstamo.
  * **Botón "Crear Plan de Pagos":** Disponible cuando el préstamo está en estado `Activo`.
  * Capacidad para generar tablas de amortización (Francés/Alemán) o definir planes de pago manuales/específicos para cada préstamo.
* **Beneficio:** Comparación precisa entre lo planificado en el plan de pagos vs. los pagos reales ejecutados.

### 2. Reporte PDF: Estado de Cuenta

* **Objetivo:** Generar un documento imprimible para el acreedor o para archivo físico.
* **Contenido:** Encabezado con datos del préstamo, resumen de saldos y una tabla detallada con el historial de desembolsos y pagos realizados.

### 3. Alertas de Vencimiento Automatizadas

* **Objetivo:** Notificar a los usuarios responsables cuando una cuota está por vencer.
* **Implementación:** Acción planificada (Cron) que revise las fechas de vencimiento y envíe una actividad o correo si faltan X días.

---

## Ideas para el Futuro (Backlog)

* **Refinanciamiento:** Un asistente para renegociar la deuda (cambiar plazos, aumentar monto) sin perder el historial contable.
* **Provisión de Intereses:** Generación automática de asientos de "Intereses por Pagar" a fin de mes, para contabilidad devengada (accrual basis), independiente del flujo de caja del pago.
* **Dashboard Financiero:** Métricas agregadas de deuda total por acreedor, flujo de caja proyectado y costos financieros totales.
