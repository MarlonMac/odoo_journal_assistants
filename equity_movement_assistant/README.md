# Asistente de Movimientos de Patrimonio

Este módulo proporciona un formulario seguro y simplificado para registrar transacciones de patrimonio, como aportes de capital de socios o la **declaración** de pago de dividendos.

Forma parte del "Ecosistema de Asistentes de Asientos Contables" y su objetivo es dar un marco de control a operaciones contables de alta importancia.

## Características Principales

- **Flujo Contable de 2 Pasos:** El asistente maneja la **declaración** de un movimiento de patrimonio, creando la deuda (pasivo) o el ingreso de capital. El **pago** de esa deuda se realiza posteriormente a través del botón "Registrar Pago".
- **Flujo de Trabajo por Categorías:** Permite preconfigurar diferentes tipos de movimientos (dividendos, aportes), asignando las cuentas de patrimonio y pasivo correctas para evitar errores.
- **Asientos Contables Precisos:** Genera el asiento de declaración para dividendos (Débito a Patrimonio, Crédito a Pasivo) o el asiento de aporte (Débito a Banco, Crédito a Patrimonio).
- **Integración con Flujo de Aprobación:** Todos los movimientos deben pasar por el flujo de aprobación antes de ser registrados contablemente.

## Configuración

1. **Crear Categorías:** Un contador debe ir a **Asistentes de Diario > Configuración > Categorías de Movimientos de Patrimonio**.
2. Ahí, debe crear las categorías necesarias. Por ejemplo:
    - **Nombre:** "Declaración de Dividendos"
        - **Tipo:** `Salida (Declaración de Dividendos)`
        - **Cuenta de Patrimonio:** `Utilidades Retenidas`
        - **Cuenta de Pasivo:** `Dividendos por Pagar`
    - **Nombre:** "Aporte de Capital de Socios"
        - **Tipo:** `Entrada (Aportes de Capital)`
        - **Cuenta de Patrimonio:** `Capital Social`

## Uso

1. Navega a **Asistentes de Diario > Movimientos de Patrimonio**.
2. Crea un nuevo registro para la **declaración**.
3. Selecciona la **Categoría** del movimiento, el **Socio** y el **Monto**.
4. Adjunta el acta o documento de respaldo y envía para aprobación.
5. Una vez aprobado y registrado contablemente, aparecerá el botón **"Registrar Pago"** para saldar la deuda generada.
