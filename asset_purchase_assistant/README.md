# Asistente de Compra de Activos

Este módulo proporciona un formulario simplificado para registrar la compra de activos fijos (equipo de cómputo, vehículos, mobiliario, etc.), generando el asiento de diario inicial para su posterior gestión contable.

Forma parte del "Ecosistema de Asistentes de Asientos Contables".

## Dependencias Clave

Este módulo **requiere** que el siguiente módulo de terceros esté instalado y funcional en tu base de datos:

* **Basic Accounting Kit** de Cybrosys Technologies.
  * Puedes descargarlo desde la Odoo App Store: [https://apps.odoo.com/apps/modules/16.0/base_accounting_kit](https://apps.odoo.com/apps/modules/16.0/base_accounting_kit)

El asistente está diseñado para interactuar con la funcionalidad de gestión de activos que proporciona dicho módulo.

---

## Características Principales

* **Flujo de Trabajo por Categorías:** Simplifica el registro al permitir a los usuarios seleccionar una "Categoría de Activo" predefinida (ej. "Equipo de Cómputo"), la cual asigna automáticamente la cuenta contable de activo correcta.
* **Manejo de Pagos Flexibles:** Permite registrar tanto compras pagadas al instante (pago directo) como compras a crédito que generan una cuenta por pagar al proveedor.
* **Interfaz Dinámica:** El formulario se adapta, mostrando solo los campos necesarios según si la compra está pendiente de pago o no.
* **Integración con Flujo de Aprobación:** Hereda el sistema de aprobación del módulo base, permitiendo un flujo de `Borrador` > `Para Aprobar` > `Aprobado` > `Registrado`.

## Configuración

1. **Crear Categorías de Activos:** Antes de usar el asistente, un contador debe ir a **Asistentes de Diario > Configuración > Categorías de Activos**. Aquí debe crear las categorías necesarias y **asignar a cada una su cuenta contable de activo correspondiente.**
2. **Configurar Cuentas por Pagar:** Asegúrate de tener al menos una cuenta de tipo "Cuentas por Pagar" en tu plan contable.

## Uso

1. Navega a **Asistentes de Diario > Compra de Activos**.
2. Crea un nuevo registro.
3. Completa la descripción, proveedor y monto.
4. Selecciona la **Categoría de Activo**; la cuenta contable se llenará automáticamente.
5. Indica si la compra está **"Pendiente de Pago"**.
    * Si lo está, completa la **Cuenta por Pagar** y la **Fecha de Vencimiento**.
    * Si no lo está (pago directo), selecciona el **Diario de Pago** de la empresa.
6. Adjunta la factura o comprobante en el chatter.
7. Guarda y envía para aprobación.
