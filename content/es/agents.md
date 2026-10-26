Entrega el repositorio y [el prompt maestro](prompts/README-DESIGNER.md) a tu agente.
Pídele revisar comandos, pruebas y limitaciones reales antes de escribir. El prompt
produce un inventario de evidencia, una estructura editorial y el JSON del generador.

| Trabajo | Instrucción reutilizable |
|---|---|
| Diseñar un README nuevo | [Diseñador de README](prompts/README-DESIGNER.md) |
| Mejorar uno existente | [Migración de presentación](prompts/MIGRATE.md) |
| Revisar el resultado | [Revisión editorial y visual](prompts/REVIEW.md) |

[AGENTS.md](AGENTS.md) explica cómo contribuir a esta herramienta. Los
[contratos de roles](agents/README.md) separan evidencia, redacción y revisión visual.
No instalan hooks, cambian configuraciones globales ni lanzan agentes automáticamente.
