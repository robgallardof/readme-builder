**Python 3.11+ and Git. Nothing else to run the generator.**

```sh
git clone https://github.com/robgallardof/readme-builder.git
cd readme-builder
python -m readme_builder build examples/project.json --output demo
```

Open `demo/README.md` and edit a copy of [the example configuration](examples/project.json).
Set the name, tagline, colour theme, language and sections; write section copy inline
or load it from a local Markdown file. See the [authoring contract](docs/CONFIGURATION.md).

The `--output` directory contains portable Markdown and SVG files. Copy those generated
files into your project, or generate there directly after reviewing the output paths.
The CLI refuses to overwrite files it does not own. `--force` is an explicit override.
