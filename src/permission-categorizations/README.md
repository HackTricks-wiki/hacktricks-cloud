# Toestemmingsrisikoklassifikasies

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hou die gedeelde data oor toestemmingserns by wat deur [CloudPEASS](https://github.com/peass-ng/CloudPEASS) en [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) gebruik word. Wysig die kanonieke platformlêer hier, eerder as die gegenereerde kopieë in enige van die twee verbruikers.

- **Critical**: toestemmings wat direk, of byna onafhanklik, kragtige voorregte verleen, 'n identiteit skep of bevoorregte uitvoering moontlik maak.
- **High**: toegang tot sensitiewe inligting, geloofsbriewe of 'n voorwaardelike pad na voorregte-eskalasie.
- **Medium**: DoS/Break, ontwrigting van bedrywighede, gewone veranderinge of voorwaardelike vermoëns sonder 'n bewese pad na sensitiewe data of voorregte.
- **Low**: gewone ontdekking en toegang tot metadata.

Daar is een kanonieke YAML-lêer per platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) en [Kubernetes](k8s.yaml). Dit is masjienleesbare lêers; die platformbladsye vertoon hul volledige YAML in die blaaier en verduidelik hoe om dit te wysig. Die ingebedde kyker gebruik die boek se kopie, terwyl die PEASS-werkvloeie die kanonieke lêers vanaf GitHub haal.

## Lêers van wolkverskaffers

`version` en `provider` identifiseer die skema. `permission_categories` bevat die vier afsonderlike lyste van toestemmings. Skuif 'n toestemming tussen lyste om die gradering daarvan te verander. AWS- en Azure-passing ignoreer hooflettergebruik; GCP-passing behou hooflettergebruik. Aliasse wat verskil slegs in hooflettergebruik, mag binne dieselfde erns herhaal word, maar botsende graderings word verwerp.

`severity_overrides` bevat geouditeerde uitsonderings op generiese reëls. As 'n uitsondering ook in die katalogus voorkom, moet albei inskrywings ooreenstem. `severity_caps` keer dat 'n kombinasie die gradering van sekere toestemmings verhoog. `non_permission_identifiers` sluit gedokumenteerde API-metodename, voorwaardesleutels en ander stringe uit wat nie werklike magtigingstoestemmings is nie.

`combinations.critical` en `combinations.high` is lyste van toestemmingslyste: elke element in 'n binneste lys moet toegeken wees voordat daardie kombinasie geld. Hou kombinasies bymekaar; as jy hulle in individuele toestemmings opdeel, sal die risiko oorskat word. Bestaande presiese- en reguliere-uitdrukkingsvelde bly die terugval vir toestemmings wat nie in die katalogus voorkom nie. 'n Volledige herskrywing van die klassifiseerder of nuwe passingsgedrag vereis steeds kodeveranderinge in die verbruikers.

## Kubernetes-lêer

`rules` is georden: die eerste reël wat pas, word gebruik. Elke reël het 'n unieke `id`, 'n `match`, 'n `severity` en 'n beskrywing in gewone taal. Voeg 'n meer spesifieke reël voor 'n breër een, of verander die erns van 'n bestaande reël. Behou die laaste onvoorwaardelike terugval.

Passings gebruik `all`, `any` en `not` vir samestelling, of 'n vergelyking met `field`, `op` en `value`. Beskikbare velde is `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL vir nie-hulpbronne in kleinletters), `non_resource_url`, `mode` en `delegated_verb`. Bewerkings is `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` en `truthy` (geen waarde word vereis nie). `always: true` pas by alles. Waardes vir group, resource, subresource en verb is in kleinletters. 'n Letterlike wildcard word as `'*'` geskryf; passing by 'n wildcard-toekenning word uitdruklik in die reëls aangedui, eerder as deur shell-patroonuitbreiding.

`severity_when` kies opsioneel 'n ander erns vir 'n voorwaarde wat pas. `severity: delegated` is gereserveer vir beperkte nabootsing: die `delegated_severities`-kaart koppel die klassifikasie van die gedelegeerde aksie aan die voorwaardelike gradering. Beskrywingsplekhouers kan na die beskikbare velde verwys, soos `{full}` en `{verb}`. Die reëls is data en word nooit as Python- of shell-kode uitgevoer nie.

## Validering en sinchronisering

Voer `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` met PyYAML geïnstalleer uit voordat jy veranderinge indien. Die boek se pull-request-werkvloei voer dieselfde validering uit.

Elke Maandag haal albei verbruikersbewaarplekke die huidige `master` van hierdie boek uit, valideer al vier lêers, vergelyk SHA-256-hashes en werk hul saamgebondelde YAML-lêers en gegenereerde ou lyste by. 'n Bronmanifes teken die boekweergawe en die hash van elke lêer aan. Onverwante veranderinge aan die boek lei nie tot 'n commit in 'n verbruiker nie. Elke werkvloei ondersteun ook 'n handmatige uitvoering. Toetse word uitgevoer voordat die werkvloei veranderde data na die verbruiker se verstektak commit; as toetse misluk, bly daardie tak onveranderd. Die verbruikers gebruik steeds hul saamgebondelde kopieë vanlyn tussen bywerkings.

Om plaaslik in 'n verbruiker by te werk, voer `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` uit. Voeg `--check` by om verouderde kopieë op te spoor sonder om dit te wysig.

Die bronaflaai in albei verbruikers probeer vyf keer weer, met beperkte afhaaltydperke en toenemende vertragings. Onvolledige aflaaie bly in tydelike gidse; as alle herpogings misluk, bly die bestaande saamgebondelde data onveranderd.
{{#include ../banners/hacktricks-training.md}}
