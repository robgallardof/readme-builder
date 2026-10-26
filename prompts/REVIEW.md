# Reusable prompt: review a README

Review this README against its repository and generated SVG components.

- Is the purpose clear on the first screen? Can a new user reach a useful result?
- Do commands and features exist? Which claims have actual evidence? Which were not tested?
- Do local links, language switches and stable anchors resolve?
- Are icons SVG rather than emoji? Are literal examples preserved?
- Do light/dark variants have readable text, useful alt text and no clipped labels?
- Does the 375px view retain essential information in normal Markdown?
- Are diagrams useful, metrics explicitly sourced and terminal output honestly labelled?
- Can another contributor regenerate the assets from the committed source?
- Are there private details or unrelated edits in the proposed commit?

Run `build CONFIG --output ROOT --check`, `check ROOT` and the project's required tests.
Open the SVG proof sheet; distinguish component rendering from a verified GitHub page.
Give concrete findings with file references. Fix authorized issues and rerun affected checks.
