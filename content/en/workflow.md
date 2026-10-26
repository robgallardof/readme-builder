```sh
# Generate the builder's own English and Spanish READMEs.
python -m readme_builder build readme.json --output .

# Detect stale generated files without writing.
python -m readme_builder build readme.json --output . --check

# Audit local links, anchors and presentation.
python -m readme_builder check .

# Make a local component proof sheet, including both colour modes.
python -m readme_builder preview . --output preview.html
```

Edit `readme.json` and `content/`, then rebuild. A SHA-256 ownership manifest protects
generated files from accidental replacement of manual edits. It is a drift/ownership
guard, not a signature or a substitute for Git. Generation does not delete stale assets.

Use `audit ROOT --json` for a machine-readable review. `audit` reports findings and exits
successfully; `check` exits 1 if any finding remains. Invalid input exits 2.
