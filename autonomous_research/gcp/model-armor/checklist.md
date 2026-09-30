# Model Armor — open leads

- [x] Verify whether a broad partial-match regex is accepted and whether it silently overrides a high-confidence PI/JB finding. Confirmed with `(?s).*`; shipped as expected template-scoped defense evasion.
- [ ] Repeat the matrix for `RESPONSIBLE_AI` and confirm that one matching exclusion suppresses all configured RAI categories exactly as documented. Use only synthetic text and delete the template.
- [ ] Test dictionary normalization/boundaries, catastrophic-regex resistance, maximum-size rules, invalid UTF-8/multibyte handling and the documented 0.5 MB evaluation limit. Performance or filter-skipping results with security impact are private-first.
- [ ] Compare direct, Agent Gateway, Apigee, Gemini Enterprise and Vertex inline integrations for cached-template propagation and non-streaming parity. Do not claim a bypass unless the fixed template or floor policy is actually skipped unexpectedly.
- [ ] Capture current UpdateTemplate and sanitize audit/platform entries with logging enabled in a disposable template. Verify request-field redaction and confirm there is no exclusion-override field in delivered logs, then delete the template and restore audit settings.
