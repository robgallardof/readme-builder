```sh
python -m unittest discover -s tests -v
python -m readme_builder build readme.json --output . --check
python -m readme_builder check .
```

Tests use actual temporary files and CLI subprocesses: deterministic output, overwrite
protection, path boundaries, escaping, colour themes, migration idempotence, code fences,
Unicode, BOM/CRLF and error exits. CI runs the same checks on Windows, Linux and macOS.
See [verification status](docs/STATUS.md) for what actually ran.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before adding a component. Keep new components
portable, accessible and useful outside a single repository.

[MIT](LICENSE) · Original icons and SVG components by Roberto Gallardo.
