# Model Armor — tested

## 2026-09-29 — template-specific catch-all exclusion

- Enabled Model Armor from a disabled baseline and created one disposable `us-central1` template
  with only prompt-injection/jailbreak enforcement at `LOW_AND_ABOVE`.
- Sanitizing Google's documented test prompt returned `MATCH_FOUND`, `EXECUTION_SUCCESS`, and HIGH
  confidence for the prompt-injection/jailbreak filter.
- Patched only `filterConfig.filterRuleSettings` with one partial-match `(?s).*` regex for
  `PROMPT_INJECTION_AND_JAILBREAK`. The API accepted the catch-all without narrowing or rejecting it.
- Repeating the identical sanitization returned overall `NO_MATCH_FOUND`; the PI/JB result was also
  `NO_MATCH_FOUND`, its previous confidence disappeared, and neither the response nor any nested
  field identified the exclusion override. This matches Google's explicit documented contract.
- Classified the behavior as expected template-scoped defense evasion, not a vulnerability. It does
  not affect streaming sanitization, other templates, floor settings, SDP, malicious URI or CSAM.
- Corrected the book's old placeholder audit method names to the exact v1 Model Armor methods and
  separated the broad floor-setting attack from the quieter template-exclusion technique.
- Cleanup deleted the template, disabled Model Armor back to baseline, removed the generated Model
  Armor service-agent binding/account, and deleted all local responses. Cloud Asset, API, IAM and
  service-account checks found no active residue.
