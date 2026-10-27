# Contributing

Use Python 3.11+ and keep runtime dependencies in the standard library. Add components
only when they have a clear authoring contract and a second realistic example.

```sh
python -m unittest discover -s tests -v
python -m readme_builder build readme.json --output .
python -m readme_builder build readme.json --output . --check
python -m readme_builder check .
python -m readme_builder preview . --output preview.html
```

Test real temporary files and CLI processes for changes to generation, migration and
ownership. Visually inspect both modes for SVG changes. Commit authored JSON/Markdown
and regenerated outputs together. Keep the license of any new artwork explicit.
Original artwork is preferred to copying a third-party icon collection.

## Commit language

All new Git commit subjects and bodies must be written in English, including merge
and squash messages. Keep the repository's existing message conventions.
This applies to all contributors and coding agents, and only to new commits.
Do not rewrite existing history to translate commit messages.
