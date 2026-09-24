# Stream Analytics — Tests Done

Wiki: `az-stream-analytics-*` (privesc/post).

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `streamingjobs/Write` full-job rewrite + MI attach | that action | DOC-ONLY |
| 2 | `inputs/Write` MSI confused-deputy read | that action | DOC-ONLY |
| 3 | `functions/Write` Azure ML UDF endpoint repoint (exfil/SSRF) — JS/C# UDFs sandboxed = NO RCE | that action | DOC-ONLY |
| 4 | `locations/SampleInput/action` job-less egress/cred-validation proxy (low-priv Query Tester role) | that action | DOC-ONLY |

Notes: `transformations/RetrieveDefaultDefinition`, scale — peripheral.
