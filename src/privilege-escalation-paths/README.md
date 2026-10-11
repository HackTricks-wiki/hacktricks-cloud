# Njia za privilege escalation

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hudumisha katalogi ya privilege escalation inayosomeka na mashine, inayotumiwa na [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Kila technique inaeleza ruhusa ambazo principal lazima iwe nazo kwa ufanisi, na kwenye rasilimali zipi, ili kupata privileges za principals lengwa. Blue-CloudPEASS hutathmini entries hizi offline dhidi ya snapshot ya inventory inayosomeka pekee, kisha huchora njia za mashambulizi kutoka principal moja hadi nyingine, ikionyesha policy au binding inayotoa ruhusa kama ushahidi, pamoja na mitigation inayoondoa njia hiyo. Hariri faili kuu hapa, badala ya nakala zilizo kwa mtumiaji.

Entries hueleza masharti ya awali, targets zinazoweza kufikiwa na mitigation pekee. Hazina commands, payloads au hatua za utekelezaji; ukurasa wa HackTricks uliounganishwa unaeleza technique.

## Muundo

Kuna directory moja kwa kila platform (`aws`, `gcp`, `azure`, `k8s`) na faili moja ya `<service>.yaml` kwa kila service, kila moja ikiwa na orodha ya techniques katika YAML. Faili zinazoitwa `_excluded*.yaml` huorodhesha techniques za HackTricks zilizokaguliwa ambazo hazina entry kimakusudi, kama vile post-exploitation, persistence au techniques ambazo haziwezi kuigwa kutokana na configuration, pamoja na sababu. `privesc-technique.schema.json` ni JSON Schema iliyohamishwa kwa ajili ya kukamilisha na kuthibitisha entries kwenye editor.

## Sehemu za technique

- `id`: kitambulisho cha kipekee duniani kote, herufi ndogo na kebab-case, chenye platform kama kiambishi awali.
- `provider`, `service`, `title` na `summary`: sentensi moja inayoeleza kile chanzo kinachopata.
- `source`: ukurasa na anchor ya HackTricks inayorekodi technique, kulingana na njia ya relative ndani ya kitabu hiki. `source_revision` ni commit ya kitabu iliyosomwa.
- `requires`: permissions ambazo source lazima iwe nazo. `all_of` huorodhesha kila kipengee kinachohitajika, na `any_of` huorodhesha mbadala. Vipengee vya AWS na GCP hutumia `action` na `resource`; vya Azure hutumia `action` (au `data_action`) na `scope`; vya Entra ID hutumia `entra_permission` au `entra_role`; na vya Kubernetes hutumia `verb`, `resource`, `subresource`, `api_group` na `namespace`. Placeholders kama `{target.arn}` huunganisha sharti na target.
- `target`: `kind` ya target, `selector` yenye masharti ambayo yote lazima yatimizwe ili principal iweze kufikiwa, na `scope` yake.
- `conditions` na `blockers`: mambo yanayoweza kuzuia njia katika uhalisia, kama vile condition keys, SCPs, boundaries au admission policies.
- `confidence`, `severity`, `mitigation`, `references` na `notes` za hiari.

Fields, target kinds, selector keys na placeholders zisizojulikana hukataliwa badala ya kupuuzwa, ili entry isiweze kupanua au kupunguza kimyakimya seti yake ya targets. Kwanza ongeza usaidizi wa selector mpya kwenye evaluator ya mtumiaji.

## Uthibitishaji na usawazishaji

Endesha `python scripts/validate_privesc_paths.py --book-root .` ukiwa na PyYAML iliyosakinishwa kabla ya kuwasilisha mabadiliko. Hufanya ukaguzi wa muundo wa directory, kila entry kwa kutumia strict loader ya evaluator (`scripts/privesc_paths_schema.py`, nakala ya moduli ya schema ya Blue-CloudPEASS), upekee wa ids, kuwepo kwa kila ukurasa wa `source` ndani ya kitabu hiki, na ikiwa JSON Schema ni ya sasa. Workflow ya pull request ya kitabu huendesha uthibitishaji huohuo.

Kila Jumatatu, Blue-CloudPEASS hu-checkout `master` ya sasa ya kitabu hiki, huthibitisha faili hizi, na kulinganisha SHA-256 hash ya kila faili na hash zilizorekodiwa wakati wa usawazishaji uliotangulia. Nyongeza, masasisho na ufutaji kutoka upstream huchukua nafasi ya nakala za mtumiaji ambazo hazijabadilika. Faili iliyobadilishwa pande zote mbili huripotiwa kama mgongano, na technique ids haziondolewi kamwe bila ledger iliyokaguliwa waziwazi. Maudhui batili au jaribio lililoshindwa huacha default branch ya mtumiaji bila mabadiliko. Mabadiliko yasiyohusiana kwenye kitabu hayasababishi commit kwenye mtumiaji.

{{#include ../banners/hacktricks-training.md}}
