# Textract completed-job result boundary — documentation audit 2026-09-26

## Result

The existing cross-principal result-retrieval technique also applies to the two asynchronous lending
getters, not only text, analysis, and expense jobs:

- `GetDocumentTextDetection`
- `GetDocumentAnalysis`
- `GetExpenseAnalysis`
- `GetLendingAnalysis`
- `GetLendingAnalysisSummary`

Each action uses `Resource: "*"`. A caller with the matching getter and a known, unexpired, same-Region
job ID does not need the corresponding `Start*` permission, a Textract list action, or access to the
original S3 object. This permits disclosure of the retained result when a job ID leaks across trust
boundaries.

AWS documents that all Textract operations are logged by CloudTrail. The page now includes the exact
prerequisites, potential impact, stealth assessment, and technique-local management-event table. No
AWS resource or paid document-analysis job was created for this metadata/coverage correction.

## Sources

- <https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazontextract.html>
- <https://docs.aws.amazon.com/textract/latest/dg/API_GetLendingAnalysis.html>
- <https://docs.aws.amazon.com/textract/latest/dg/API_GetLendingAnalysisSummary.html>
- <https://docs.aws.amazon.com/textract/latest/dg/logging-using-cloudtrail.html>
