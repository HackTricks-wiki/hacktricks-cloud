# ECR `BatchGetImage` CloudTrail audit — 2026-09-26

The book said both that `BatchGetImage` had not appeared in Event History during a previous test and that *every* ECR API call always appears there. The latter is an unjustified blanket claim. [AWS's ECR CloudTrail guide](https://docs.aws.amazon.com/AmazonECR/latest/userguide/logging-using-cloudtrail.html) explicitly gives a `BatchGetImage` CloudTrail example. The [CloudTrail data-event resource catalog](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-events.html) does not offer an ECR selector, so ECR control-plane API logging belongs to management events.

Live retest in the authorized account: assumed `ChackBotAdministratorRole` in `us-east-1`; created an isolated `ht-ecr-cloudtrail-audit-*` repository, pushed local Alpine, successfully called `BatchGetImage` by tag, and immediately queried Event History. The immediate lookup returned no event for the new repository. A later lookup found **two** `BatchGetImage` events naming that exact repository, both with `eventCategory: Management` and event times around the test call. The previously suspected silent step was normal CloudTrail delivery latency, not a reliable blind spot.

Cleanup verified: the temporary ECR repository was force-deleted, its local image tag removed, and the Docker registry login removed. No test infrastructure remains.

| Candidate | Result | Next action |
| --- | --- | --- |
| ECR `BatchGetImage` is a reliable CloudTrail blind spot | Negative; two test events appeared after delivery | Do not publish as a stealth technique |
| ECR has a CloudTrail data-event selector | Negative in current CloudTrail catalog | Keep ECR control-plane logs classified as management events |
