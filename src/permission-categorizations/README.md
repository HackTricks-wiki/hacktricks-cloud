# Uainishaji wa hatari za permissions

HackTricks Cloud hudumisha data ya pamoja ya severity ya permissions inayotumiwa na [CloudPEASS](https://github.com/peass-ng/CloudPEASS) na [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Hariri faili kuu ya platform hapa, badala ya nakala zilizozalishwa katika consumer yoyote.

- **Critical**: permissions zinazotoa moja kwa moja, au karibu bila kutegemea masharti mengine, privileges zenye nguvu, kuunda identity, au kuwezesha privileged execution.
- **High**: ufikiaji wa taarifa nyeti, credentials, au njia ya conditional privilege escalation.
- **Medium**: DoS/Break, kuvuruga utendakazi, mabadiliko ya kawaida, au capabilities zenye masharti bila njia iliyoonyeshwa ya kufikia data nyeti au privilege.
- **Low**: ugunduzi wa kawaida na ufikiaji wa metadata.

Kuna faili moja kuu ya YAML kwa kila platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), na [Kubernetes](k8s.yaml). Haya ni mafaili yanayosomeka na mashine; kurasa za platform huonyesha YAML yake kamili kwenye browser na kueleza jinsi ya kuyahariri. Inline viewer hutumia nakala ya kitabu, huku workflows za PEASS zikichukua mafaili kuu kutoka GitHub.

## Mafaili ya cloud provider

`version` na `provider` hutambulisha schema. `permission_categories` ina orodha nne za permissions za kibinafsi. Hamisha permission kati ya orodha ili kubadilisha rating yake. Ulinganishaji wa AWS na Azure hupuuza case; ulinganishaji wa GCP huhifadhi case. Case aliases zinaweza kujirudia ndani ya severity ileile, lakini ratings zinazokinzana hukataliwa.

`severity_overrides` ina exceptions zilizokaguliwa kwa rules za jumla. Ikiwa exception pia ipo kwenye catalog, entries zote mbili lazima zikubaliane. `severity_caps` huzuia combination kuongeza rating ya permissions zilizochaguliwa. `non_permission_identifiers` huondoa majina ya API-method yaliyoandikwa, condition keys, na strings nyingine ambazo si permissions halisi za authorization.

`combinations.critical` na `combinations.high` ni orodha za lists za permissions: kila kipengele cha inner list lazima kiwe kimepewa ili combination hiyo itumike. Hifadhi combinations pamoja; kuzigawanya kuwa grants za kibinafsi kungeonyesha hatari iliyozidi. Fields zilizopo za exact na regular-expression zinaendelea kuwa fallback kwa permissions ambazo hazipo kwenye catalog. Uandishi upya kamili wa classifier au tabia mpya ya matching bado unahitaji mabadiliko ya code katika consumers.

## Faili ya Kubernetes

`rules` imepangwa kwa mpangilio: rule ya kwanza inayolingana ndiyo hushinda. Kila rule ina `id` ya kipekee, `match`, `severity`, na `description` katika lugha rahisi. Ongeza rule maalum zaidi kabla ya rule pana zaidi, au badilisha severity ya rule iliyopo. Hifadhi fallback ya mwisho isiyo na masharti.

Matches hutumia `all`, `any`, na `not` kwa composition, au comparison ya `field`, `op`, na `value`. Fields zinazopatikana ni `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode`, na `delegated_verb`. Operations ni `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, na `truthy` (haihitaji value). `always: true` hulinganisha kila kitu. Values za group, resource, subresource, na verb ni lowercase. Wildcard halisi huandikwa kama `'*'`; matching ya wildcard grant imeainishwa wazi katika rules, badala ya shell pattern expansion.

`severity_when` huchagua kwa hiari severity nyingine kwa condition inayolingana. `severity: delegated` imetengwa kwa constrained impersonation: map ya `delegated_severities` hubadilisha classification ya delegated action kuwa rating ya masharti. Placeholders za description zinaweza kurejelea fields zinazopatikana, kama vile `{full}` na `{verb}`. Rules ni data na hazitathminiwi kamwe kama Python au shell code.

## Uthibitishaji na synchronization

Endesha `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` ukiwa na PyYAML iliyosakinishwa kabla ya kuwasilisha mabadiliko. Workflow ya pull-request ya kitabu huendesha uthibitishaji huohuo.

Kila Jumatatu, repositories zote mbili za consumer huchukua `master` ya sasa ya kitabu hiki, huthibitisha mafaili yote manne, hulinganisha hashes za SHA-256, na kusasisha mafaili yao ya YAML yaliyofungwa pamoja na lists za zamani zilizozalishwa. Source manifest huhifadhi revision ya kitabu na hash ya kila faili. Mabadiliko yasiyohusiana kwenye kitabu hayazalishi consumer commit. Kila workflow pia inaruhusu run ya manual. Tests huendeshwa kabla workflow haijafanya commit ya data iliyobadilika kwenye default branch ya consumer; kushindwa huacha branch hiyo bila mabadiliko. Consumers huendelea kutumia nakala zao zilizofungwa offline kati ya updates.

Ili kusasisha locally katika consumer, endesha `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Ongeza `--check` ili kugundua nakala zilizopitwa na wakati bila kuziandika.

Kuchukua source katika consumers zote mbili hujaribu mara tano tena kwa checkout deadlines zenye mipaka na delays zinazoongezeka. Downloads zisizokamilika hubaki katika temporary directories; retries zikimalizika, data iliyopo iliyofungwa hubaki bila kubadilishwa.
