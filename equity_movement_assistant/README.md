# Asistente de Movimientos de Patrimonio

Este módulo proporciona un formulario seguro y simplificado para registrar transacciones de patrimonio, como aportes de capital de socios o el pago de dividendos y reparto de utilidades.

Forma parte del "Ecosistema de Asistentes de Asientos Contables" y su objetivo es dar un marco de control a operaciones contables de alta importancia.

## Características Principales

- **Flujo de Trabajo por Categorías:** Permite preconfigurar diferentes tipos de movimientos (dividendos, aportes), asignando la cuenta de patrimonio correcta y el tipo de transacción (entrada o salida) para evitar errores.
- **Asientos Contables Precisos:** Genera automáticamente el asiento de diario correcto según si es un aporte (Débito a Banco, Crédito a Patrimonio) o un dividendo (Débito a Patrimonio, Crédito a Banco).
- **Trazabilidad del Socio:** Requiere la selección de un Socio o Accionista (`res.partner`) para cada transacción.
- **Integración con Flujo de Aprobación:** Todos los movimientos deben pasar por el flujo de aprobación (`Borrador` > `Para Aprobar` > `Aprobado`) antes de poder ser registrados contablemente.

## Configuración

1. **Crear Categorías:** Antes de usar el asistente, un contador debe ir a **Asistentes de Diario > Configuración > Categorías de Movimientos de Patrimonio**.
2. Ahí, debe crear las categorías necesarias. Por ejemplo:
    - **Nombre:** "Pago de Dividendos de Utilidades Retenidas"
        - **Tipo:** `Salida (Pago de Dividendos)`
        - **Cuenta de Patrimonio:** `Utilidades Retenidas`
    - **Nombre:** "Aporte de Capital de Socios"
        - **Tipo:** `Entrada (Aportes de Capital)`
        - **Cuenta de Patrimonio:** `Capital Social`

## Uso

1. Navega a **Asistentes de Diario > Movimientos de Patrimonio**.
2. Crea un nuevo registro.
3. Selecciona la **Categoría** del movimiento. El tipo y la cuenta se llenarán automáticamente.
4. Asigna el **Socio / Accionista** y el **Monto**.
5. Selecciona el **Diario de Pago/Cobro** (Banco o Caja).
6. Adjunta el acta o documento de respaldo en el chatter.
7. Guarda y envía para aprobación.
