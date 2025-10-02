# Asistente de Gastos Corporativos

Este módulo proporciona un formulario simplificado para registrar gastos operativos, reembolsos a empleados y facturas de proveedores que no requieren el proceso completo de una factura de compra.

Forma parte del "Ecosistema de Asistentes de Asientos Contables" y depende del módulo `journal_entry_assistant_base`.

## Características Principales

- **Flujo de Trabajo por Categorías:** Simplifica la entrada de datos permitiendo a los usuarios seleccionar una categoría de gasto (ej. "Combustible"), la cual asigna automáticamente la cuenta contable correcta.
- **Gestión de Cuentas por Pagar:** Permite registrar tanto gastos pagados al instante como facturas o reembolsos que quedan como una deuda pendiente.
- **Adjunto Requerido:** Asegura que cada gasto tenga un respaldo digital al hacer obligatorio adjuntar un comprobante.
- **Asignación de Responsables:** Permite asignar uno o más empleados a un gasto.
- **Integración con Contabilidad Analítica:** Permite etiquetar gastos por sucursal, departamento o centro de costo.

## Configuración

### Configuración Multi-Empresa

**Este módulo es totalmente compatible con entornos multi-empresa.**

- Las **Categorías de Gastos** son específicas para cada compañía. Al crear una nueva categoría, esta se asignará automáticamente a la compañía activa del usuario.
- El asistente solo mostrará y permitirá seleccionar las categorías pertenecientes a la misma compañía del registro del asistente.
- Las cuentas contables y diarios también son filtrados por compañía para garantizar la integridad de los datos.

### Configuración de Cuentas

1. **Crear Categorías de Gastos:** Antes de usar el asistente, un contador debe ir a **Asistentes de Diario > Configuración > Categorías de Gastos** y crear las categorías que la empresa necesita. **Es crucial asignar a cada categoría su cuenta contable de gasto correspondiente.**
2. **Configurar Cuentas por Pagar:** Asegúrate de tener al menos una cuenta de tipo "Cuentas por Pagar" en tu plan contable para usar el flujo de reembolsos.

## Uso

1. Navega a **Asistentes de Diario > Gastos Corporativos**.
2. Crea un nuevo registro.
3. Selecciona la **Categoría**, rellena la descripción y el monto.
4. Si es una factura pendiente o un reembolso, marca la casilla **"Es Cuenta por Pagar"** y especifica a quién se le debe. Si es un pago directo, selecciona el **Diario de Pago** de la empresa.
5. Adjunta el recibo o factura en el chatter.
6. Guarda y haz clic en **Registrar**.
