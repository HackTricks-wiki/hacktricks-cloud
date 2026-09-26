# Stream Analytics — Tests Done

Wiki: `az-stream-analytics-*` (privesc/post).

| # | Technique | Min perms | Status |
|---|-----------|-----------|--------|
| 1 | `streamingjobs/Write` full-job rewrite + MI attach | that action | DOC-ONLY |
| 2 | `inputs/Write` MSI confused-deputy read | that action | DOC-ONLY |
| 3 | `functions/Write` Azure ML UDF endpoint repoint (exfil/SSRF) — JS/C# UDFs sandboxed = NO RCE | that action | DOC-ONLY |
| 4 | `locations/SampleInput/action` job-less egress/cred-validation proxy (low-priv Query Tester role) | that action | **PARTIAL — min-perms + job-less outbound attempt confirmed 2026-09-25; full data-return not reproduced** |
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

**Lab record (test #4, 2026-09-25 — SampleInput job-less proxy, PARTIAL):** RG `htrc-sasample`, StorageV2 `htsasample31607`,
container `samplein`, blob `data.json` holding a known marker + fake `db_password`. **Confirmed:** (a) min-perms — the
built-in **low-priv `Stream Analytics Query Tester`** role's action list includes `Microsoft.StreamAnalytics/locations/SampleInput/action`
(alongside CompileQuery/TestQuery/OperationResults), so no Contributor needed; (b) the action is **job-less** and accepted with
**HTTP 202** (async op under `locations/eastus/OperationResults/...`); (c) the SA service **attempts an outbound connection to the
caller-supplied datasource with caller-supplied creds** — the op reached status `ErrorConnectingToInput`
(`InternalServerError: Unexpected error while getting input samples`), i.e. it tried to connect. **Contract nuance discovered:**
SampleInput needs a **flat top-level `serialization` `{"type":"Json","encoding":"UTF8"}`** (NOT the nested `{properties:{...}}`
shape — that throws `BaseEventSerializationProperties ... abstract class`), plus top-level `eventStartTime`/`eventEndTime` and
`input.properties.serialization`. **NOT reproduced:** a successful sampled-data return — the 2017-04-01-preview blob-sampling
path returned `ErrorConnectingToInput` on a fully-reachable StorageV2 (shared-key + public access on, defaultAction Allow, blob
readable via the same key), across repeated attempts and with/without date-path tokens; looks like preview-endpoint flakiness
rather than a config error, but left **unproven** — did NOT upgrade the wiki's data-return claim. **Teardown:** `az group delete htrc-sasample`.
