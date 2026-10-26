Already have a README you like? Start with a dry run:

```sh
python -m readme_builder migrate /path/to/project/README.md
python -m readme_builder migrate /path/to/project/README.md --write
python -m readme_builder check /path/to/project
```

Decorative Unicode emoji and supported shortcodes become local line icons. Ordinary
fenced examples and inline code remain unchanged. Mermaid labels become plain text,
because image HTML is not portable inside those labels. Heading aliases preserve
existing navigation. UTF-8 BOM and CRLF/LF are retained.

The audit reports broken local links, unresolved merge markers and remaining decorative
emoji. It does not fetch remote links or decide whether a project's claims are true.
For complex nested Markdown, review the diff: this is a conservative scanner, not a
complete Markdown parser. Keep a Git commit before applying a large migration.
