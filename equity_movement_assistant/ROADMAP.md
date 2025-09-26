# Roadmap: Asistente de Movimientos de Patrimonio

El desarrollo futuro de este módulo se centrará en mejorar el seguimiento y la reportería.

## v1.1.0 (Planeado)

### Reporte de Movimientos por Socio

* **Descripción:** Crear un reporte en PDF que permita seleccionar un rango de fechas y un socio para generar un estado de cuenta de sus aportes y dividendos declarados/pagados.
* **Beneficio:** Facilitaría la preparación de informes para juntas directivas o para los propios accionistas.
* **Consideraciones Técnicas:**
  * Crear un `wizard` (modelo transitorio) para los parámetros del reporte.
  * Definir una acción de reporte (`ir.actions.report`) y su plantilla QWeb.
