# Asistente de Asientos de Diario (Base)

Este módulo es el núcleo del "Ecosistema de Asistentes de Asientos Contables". No es una aplicación funcional por sí misma, sino una base de desarrollo que proporciona una estructura y lógica común para todos los módulos de asistentes.

## Propósito

El objetivo de este módulo es la **reutilización de código** y la **estandarización**. Proporciona un modelo abstracto (`assistant.journal.entry.base`) que cualquier otro módulo puede heredar para obtener instantáneamente:

* Un flujo de estados (`Borrador`, `Para Aprobar`, `Aprobado`, `Registrado`, `Cancelado`).
* Lógica para registrar, cancelar y revertir asientos contables (`account.move`).
* Integración con el chatter de Odoo para adjuntar archivos y registrar notas.
* Un sistema de aprobación con un grupo de seguridad (`Aprobador de Asistentes de Diario`).
* Una función integrada para registrar pagos (`action_register_payment`) que reutiliza el asistente nativo de Odoo.

## Arquitectura para Desarrolladores

Para crear un nuevo asistente, tu modelo principal debe heredar de `assistant.journal.entry.base`.

```python
class MiNuevoAsistente(models.Model):
    _name = 'mi.nuevo.asistente'
    _inherit = 'assistant.journal.entry.base'
```

Deberás implementar los siguientes métodos en tu modelo para que la lógica de action\_post funcione:

* **\_get\_journal(self)**: Debe devolver el registro del account.journal que se usará para el asiento.
* **\_prepare\_move\_lines(self)**: Debe devolver una lista de tuplas con las líneas (débito y crédito) del asiento contable.
