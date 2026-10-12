# Njia za privilege escalation

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hudumisha katalogi ya privilege escalation inayosomeka na mashine, inayotumiwa na [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Kila mbinu inaeleza ruhusa ambazo principal lazima awe nazo kwa ufanisi, na kwenye rasilimali zipi, ili kupata privileges za seti ya principals lengwa. Blue-CloudPEASS hutathmini maingizo haya offline dhidi ya snapshot ya inventory inayosomeka tu, na kuchora njia za mashambulizi kutoka principal mmoja hadi mwingine, huku ikionyesha policy au binding inayotoa ruhusa kama ushahidi, na mitigation inayoondoa njia hiyo. Hariri faili za msingi hapa, badala ya nakala zilizo kwenye consumer.

Maingizo yanaeleza tu masharti ya awali, targets zinazoweza kufikiwa na mitigation. Hayana commands, payloads au hatua za utekelezaji; ukurasa wa HackTricks uliounganishwa unaeleza mbinu hiyo.

## Muundo

Kuna directory moja kwa kila platform (`aws`, `gcp`, `azure`, `k8s`) na faili moja ya `<service>.yaml` kwa kila huduma, ambayo kila moja ina orodha ya mbinu za YAML. Faili zinazoitwa `_excluded*.yaml` huorodhesha mbinu za HackTricks zilizopitiwa ambazo hazina ingizo kimakusudi, kama vile post-exploitation, persistence au mbinu ambazo haziwezi kuigwa kutokana na configuration, pamoja na sababu. `privesc-technique.schema.json` ni JSON Schema iliyohamishwa kwa ajili ya kukamilisha na kuthibitisha maudhui kwenye editor.

## Sehemu za mbinu

- `id`: ya kipekee kimataifa, herufi ndogo na kebab-case, ikiwa na platform kama kiambishi awali.
- `provider`, `service`, `title` na `summary`: sentensi moja inayoeleza kile chanzo kinachopata.
- `source`: ukurasa wa HackTricks na anchor inayoandika mbinu hiyo, kulingana na njia kutoka kwenye kitabu hiki. `source_revision` ni commit ya kitabu iliyosomwa.
- `requires`: ruhusa ambazo chanzo lazima kiwe nazo. `all_of` huorodhesha kila kipengee kinachohitajika, na `any_of` huorodhesha mbadala. Vipengee vya AWS na GCP hutumia `action` na `resource`, vipengee vya Azure hutumia `action` (au `data_action`) na `scope`, vipengee vya Entra ID hutumia `entra_permission` au `entra_role`, na vipengee vya Kubernetes hutumia `verb`, `resource`, `subresource`, `api_group` na `namespace`. Vihisishi nafasi kama `{target.arn}` huunganisha sharti na target.
- `target`: `kind` ya target, `selector` ambayo masharti yake yote lazima yatimizwe ili principal aweze kufikiwa, na `scope` yake.
- `conditions` na `blockers`: mambo yanayoweza kuzuia njia katika matumizi halisi, kama vile condition keys, SCPs, boundaries au admission policies.
- `confidence`, `severity`, `mitigation`, `references` na `notes` ya hiari.

Sehemu zisizojulikana, target kinds, selector keys na vihisishi nafasi hukataliwa badala ya kupuuzwa, kwa hiyo ingizo haliwezi kamwe kupanua au kupunguza seti ya targets kimyakimya. Kwanza ongeza uwezo wa kutumia selector mpya kwenye evaluator ya consumer.

### Viunganishi vya Schema v2

Loader ya v2 inaongeza vihisishi nafasi viwili na AWS selector moja, na inaruhusu selector iliyopo ya K8s running-pod itumike kwenye targets za GCP. Sehemu hizi zinahitaji ulinganifu kamili na inventory iliyokusanywa; inventory ikikosekana, coverage huwa unknown, si njia inayoweza kufikiwa.

| Sehemu | Matumizi na muundo unaohitajika |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` na `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Tumia pamoja kwenye target ya AWS `aws_account_admin`. Kila mbadala wa sharti lazima ujumuishe `iam:CreatePolicyVersion` kwenye kihisishi nafasi hicho. Policy lazima iwe imeambatishwa kwa role ambayo chanzo kinaweza ku-assume katika account hiyo hiyo; evaluator hukagua uwezo wa kuongeza policy version na kuhesabu upya ruhusa zinazotumika za role. `SetDefaultPolicyVersion` haijajumuishwa. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Kwenye target ya GCP `k8s_service_account` yenye `scope: cluster`, huchagua KSAs zinazotumiwa na pods zinazoendesha na zilizo na token inayopatikana katika GKE cluster inayolingana. Usiichanganye na `k8s_sa_in_cluster` au `k8s_sa_has_token_secret`. Matumizi yaliyopo ya K8s hayajabadilika. |
| `{source_rolebound_clusterrole}` | Itumie kama `resource_name` kwenye masharti ya K8s `clusterroles` yenye `api_group: rbac.authorization.k8s.io` na `namespace: "*"`. Kila mbadala unahitaji `escalate` na `update` au `patch` kwenye jina hilo hilo. Target lazima iwe `k8s_service_account` yenye `scope: same_namespace` na `selector.k8s_sa_in_namespace: "{target.namespace}"`; RoleBinding lazima imuunganishe chanzo katika namespace hiyo. |

## Uthibitishaji na usawazishaji

Endesha `python scripts/validate_privesc_paths.py --book-root .` huku PyYAML ikiwa imesakinishwa kabla ya kuwasilisha mabadiliko. Hukagua muundo wa directory, kila ingizo kwa kutumia strict loader ya evaluator (`scripts/privesc_paths_schema.py`, nakala ya moduli ya schema ya Blue-CloudPEASS), vitambulisho vya kipekee, kurasa za chanzo na heading anchors, na kuhakikisha kuwa JSON Schema ni ya sasa. Tumia `--peaso-root /path/to/Blue-CloudPEASS` ili pia kulinganisha faili zote mbili za schema byte kwa byte na zile za consumer. Workflow ya pull request ya kitabu huendesha uthibitishaji huohuo.

Kila Jumatatu, Blue-CloudPEASS huchukua `master` ya sasa ya kitabu hiki, huthibitisha faili hizi, na kulinganisha SHA-256 hash za kila faili na hash zilizorekodiwa kwenye usawazishaji uliotangulia. Nyongeza, masasisho na ufutaji kutoka upstream hubadilisha nakala za consumer ambazo hazijabadilishwa. Faili iliyobadilishwa pande zote mbili huripotiwa kama mgongano, na vitambulisho vya mbinu haviondolewi kamwe bila ledger iliyopitiwa waziwazi. Maudhui yasiyo halali au jaribio lililoshindwa huacha default branch ya consumer bila mabadiliko. Mabadiliko yasiyohusiana kwenye kitabu hayasababishi commit kwenye consumer.

{{#include ../banners/hacktricks-training.md}}
