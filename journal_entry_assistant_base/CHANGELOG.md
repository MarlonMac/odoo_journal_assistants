# Changelog

## [1.0.0] - 2025-09-23

### Added

- **Lanzamiento Inicial del Módulo Base.**
- **Modelo Abstracto `assistant.journal.entry.base`:** Proporciona la estructura de datos y lógica fundamental.
- **Flujo de Estados:** Implementación de los estados `borrador`, `registrado` y `cancelado`.
- **Acciones Base:** Métodos `action_post`, `action_cancel` y `action_to_draft` para gestionar el ciclo de vida del registro y su asiento contable asociado.
- **Patrón de Plantilla:** `action_post` utiliza los métodos `_get_journal` y `_prepare_move_lines` que deben ser implementados por los módulos herederos.
- **Integración con Chatter:** Herencia de `mail.thread` y `mail.activity.mixin`.
