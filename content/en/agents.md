Give an agent the repository and [the master prompt](prompts/README-DESIGNER.md).
Ask it to inspect actual commands, tests and limitations before writing copy. The
prompt produces an evidence inventory, a content structure and a generator config.

| Task | Reusable brief |
|---|---|
| Design a new README | [README designer](prompts/README-DESIGNER.md) |
| Upgrade an existing README | [Presentation migration](prompts/MIGRATE.md) |
| Review the result | [Editorial and visual review](prompts/REVIEW.md) |

[AGENTS.md](AGENTS.md) describes how to contribute to this tool. The
[role contracts](agents/README.md) help separate evidence, copy and visual review.
They do not install hooks, edit global settings or automatically spawn other agents.
