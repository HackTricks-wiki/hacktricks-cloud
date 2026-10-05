# Uainishaji wa hatari za permissions

HackTricks Cloud hudumisha data ya pamoja ya severity ya permissions inayotumiwa na [CloudPEASS](https://github.com/peass-ng/CloudPEASS) na [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Hariri faili kuu ya platform hapa, badala ya nakala zinazozalishwa katika consumer yoyote.

- **Critical**: permissions zinazotoa moja kwa moja, au karibu bila kutegemea masharti mengine, privileges kubwa, kuunda identity, au kuwezesha privileged execution.
- **High**: access kwa taarifa nyeti, credentials, au njia ya conditional privilege escalation.
- **Medium**: DoS/Break, usumbufu wa uendeshaji, mabadiliko ya kawaida, au capabilities zenye masharti bila njia iliyothibitishwa ya data nyeti au privilege.
- **Low**: ugunduzi wa kawaida na access ya metadata.

Kuna faili moja kuu ya YAML kwa kila platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), na [Kubernetes](k8s.yaml). Hizi ni faili zinazoweza kusomeka na mashine; kurasa za platform zinaeleza jinsi ya kuzihariri.

## Cloud provider files

`version` na `provider` hutambulisha schema. `permission_categories` huhifadhi orodha nne za permissions binafsi. Hamisha permission kati ya orodha ili kubadilisha rating yake. AWS na Azure matching hupuuza case; GCP matching huhifadhi case. Case aliases zinaweza kujirudia ndani ya severity ileile, lakini ratings zinazokinzana hukataliwa.

`severity_overrides` huwa na exceptions zilizokaguliwa kwa rules za jumla. Ikiwa exception pia ipo kwenye catalog, entries zote mbili lazima zikubaliane. `severity_caps` huzuia combination fulani kuinua permissions zilizochaguliwa. `non_permission_identifiers` huondoa majina ya API-method yaliyoandikwa, condition keys, na strings nyingine ambazo si permissions halisi za authorization.

`combinations.critical` na `combinations.high` ni orodha za permission lists: kila kipengele cha inner list lazima kiwe granted ili combination hiyo itumike. Weka combinations pamoja; kuzigawa kuwa grants binafsi kungeonyesha risk kubwa kuliko ilivyo. Fields za existing exact na regular-expression zinaendelea kuwa fallback kwa permissions ambazo hazipo kwenye catalog. Kuandika upya classifier nzima au kuongeza matching behavior mpya bado kunahitaji mabadiliko ya code katika consumers.

## Kubernetes file

`rules` zimepangwa kwa mpangilio: rule ya kwanza inayolingana ndiyo hutumika. Kila rule ina `id` ya kipekee, `match`, `severity`, na `description` iliyo katika lugha rahisi. Ongeza rule maalum zaidi kabla ya rule pana zaidi, au badilisha severity ya rule iliyopo. Hifadhi fallback ya mwisho isiyo na masharti.

Matches hutumia `all`, `any`, na `not` kwa composition, au comparison ya `field`, `op`, na `value`. Fields zinazopatikana ni `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (lowercase non-resource URL), `non_resource_url`, `mode`, na `delegated_verb`. Operations ni `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, na `truthy` (haihitaji value). `always: true` hulinganisha kila kitu. Values za group, resource, subresource, na verb ni lowercase. Wildcard halisi huandikwa kama `'*'`; matching ya wildcard grant imeainishwa wazi katika rules, badala ya shell pattern expansion.

`severity_when` kwa hiari huchagua severity nyingine kwa condition inayolingana. `severity: delegated` imehifadhiwa kwa constrained impersonation: `delegated_severities` map yake hubadilisha classification ya delegated action kuwa rating ya masharti. Placeholders za description zinaweza kurejelea fields zinazopatikana, kama `{full}` na `{verb}`. Rules ni data na hazitathminiwi kamwe kama Python au shell code.

## Validation and synchronization

Endesha `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` ukiwa na PyYAML iliyosakinishwa kabla ya kuwasilisha mabadiliko. Pull-request workflow ya book huendesha validation hiyo hiyo.

Kila Jumatatu, repositories zote mbili za consumers hu-checkout `master` ya sasa ya book hii, huthibitisha faili zote nne, hulinganisha SHA-256 hashes, na kusasisha faili zao za YAML zilizofungwa pamoja na legacy lists zinazozalishwa. Source manifest huhifadhi revision ya book na hash ya kila faili. Mabadiliko yasiyohusiana katika book hayasababishi consumer commit. Kila workflow pia inaunga mkono run ya manual. Tests huendeshwa kabla ya workflow ku-commit data iliyobadilika kwenye default branch ya consumer; failures huacha branch hiyo bila kubadilika. Consumers huendelea kutumia bundled copies zao offline kati ya updates.

Ili kusasisha locally katika consumer, endesha `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Ongeza `--check` ili kugundua copies zilizopitwa na wakati bila kuziandika.
