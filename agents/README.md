# Agent role contracts

These are reusable responsibilities, not automatic delegation or permission to contact
another agent. One agent can perform all three roles in sequence.

| Role | Inputs | Output | Boundary |
|---|---|---|---|
| Evidence editor | Source code, manifests, tests, existing docs | Verified claims and unknowns | Never convert an assumption into a measured result |
| README designer | Evidence, audience, language, original identity | JSON config and authored Markdown | Never sacrifice copyable instructions to decoration |
| Visual reviewer | Generated assets and proof sheet | Overflow/contrast/navigation findings | Distinguish local component review from GitHub rendering |

Use [the master brief](../prompts/README-DESIGNER.md),
[migration brief](../prompts/MIGRATE.md), and [review brief](../prompts/REVIEW.md).
