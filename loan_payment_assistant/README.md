# Asistente de Pago de Préstamos

Este módulo simplifica el registro de pagos de cuotas de préstamos, una tarea que de otro modo requeriría un asiento de diario manual complejo.

Forma parte del "Ecosistema de Asistentes de Asientos Contables" y depende del módulo `journal_entry_assistant_base`.

## Características Principales

- **Separación de Capital e Intereses:** Permite al usuario introducir fácilmente el monto correspondiente al capital y a los intereses de una cuota.
- **Asiento Contable de 3 Líneas:** Genera automáticamente el asiento de diario correcto, con débitos a la cuenta de pasivo (capital) y a la cuenta de gasto (intereses), y un crédito al diario de pago.
- **Gestión de Préstamos:** Introduce un modelo para registrar los diferentes préstamos de la empresa, asociando a cada uno su acreedor y sus cuentas contables específicas.
- **Integración con Flujo de Aprobación:** Al heredar del módulo base, cada pago de préstamo puede pasar por el flujo de aprobación (`Borrador` > `Para Aprobar` > `Aprobado`) antes de ser registrado.

## Configuración

### Configuración Multi-Empresa

**Este módulo es totalmente compatible con entornos multi-empresa.**

- El registro de **Préstamos** es específico para cada compañía.
- Al usar el asistente, solo se mostrarán los préstamos y diarios de pago que pertenezcan a la compañía seleccionada en el asistente.

### Configuración de Cuentas

1. **Crear Préstamos:** Antes de poder registrar un pago, un contador debe ir a **Asistentes de Diario > Configuración > Préstamos**.
2. Ahí, debe crear un registro por cada préstamo que tenga la empresa, especificando:
    - El **Acreedor** (quién otorgó el préstamo).
    - La **Cuenta de Pasivo (Capital)** donde está registrada la deuda.
    - La **Cuenta de Gasto (Intereses)** donde se registrarán los intereses.

## Uso

1. Navega a **Asistentes de Diario > Pago de Préstamos**.
2. Crea un nuevo registro.
3. Selecciona el **Préstamo** que deseas pagar.
4. Introduce el monto de **Capital** y de **Intereses** de la cuota. El total se calculará automáticamente.
5. Selecciona desde qué **Diario de Pago** (Banco o Caja) se realizó la transacción.
6. Adjunta el comprobante de pago en el chatter.
7. Guarda y envía para aprobación.
