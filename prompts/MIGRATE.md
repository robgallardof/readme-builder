# Reusable prompt: migrate presentation

Upgrade this repository's README presentation using readme-builder. Preserve the
existing prose, evidence, examples, commands and useful visual identity. Replace
decorative emoji with original SVG line icons. Do not redesign unrelated repositories.

Read the repository's rules and current worktree status. Record existing README
headings, anchors, relative image paths, Mermaid blocks and language links. Run
`python -m readme_builder migrate PATH` first, inspect the proposed scope, then apply
`--write` within the requested files. Preserve literal code examples. Review complex
Markdown and link fragments manually; the scanner is not a full Markdown parser.

Keep existing bespoke banners and widgets that already work. Reuse their palette
or select a coherent builder theme. Give essential information normal text alternatives.
Do not insert an HTML image into an attribute, URL, shell example or Mermaid label.

Run an audit, check the diff, render the changed SVGs and check the repository's required
tests. Report actual verification and unresolved issues honestly. Preserve unrelated
uncommitted work. Never push changes outside the user's selected repository scope.
