# Toestemmingsrisikokategorisering

HackTricks Cloud onderhou die gedeelde toestemmings-ernstdata wat deur [CloudPEASS](https://github.com/peass-ng/CloudPEASS) en [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) gebruik word. Wysig die kanonieke platformlêer hier, eerder as die gegenereerde kopieë in enige van die verbruikers.

- **Critical**: toestemmings wat direk, of byna onafhanklik, kragtige voorregte verleen, ’n identiteit skep, of bevoorregte uitvoering moontlik maak.
- **High**: toegang tot sensitiewe inligting, credentials, of ’n voorwaardelike privilege escalation-pad.
- **Medium**: DoS/Break, operasionele ontwrigting, gewone veranderinge, of voorwaardelike vermoëns sonder ’n gedemonstreerde pad na sensitiewe data of voorregte.
- **Low**: gewone ontdekking en toegang tot metadata.

Daar is een kanonieke YAML-lêer per platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), en [Kubernetes](k8s.yaml). Dit is masjienleesbare lêers; die platformbladsye verduidelik hoe om hulle te wysig.

## Cloud-verskafferlêers

`version` en `provider` identifiseer die skema. `permission_categories` bevat die vier individuele toestemmingslyste. Skuif ’n toestemming tussen lyste om die gradering daarvan te verander. AWS- en Azure-passing ignoreer hooflettergevoeligheid; GCP-passing behou hooflettergevoeligheid. Hoofletteraliases mag binne dieselfde ernstigheid herhaal word, maar teenstrydige graderings word afgekeur.

`severity_overrides` bevat geouditeerde uitsonderings op generiese reëls. Indien ’n uitsondering ook in die katalogus voorkom, moet albei inskrywings ooreenstem. `severity_caps` verhoed dat ’n kombinasie geselekteerde toestemmings opgradeer. `non_permission_identifiers` sluit gedokumenteerde API-metodename, voorwaardesleutels, en ander stringe uit wat nie werklike magtigingstoestemmings is nie.

`combinations.critical` en `combinations.high` is lyste van toestemmingslyste: elke element van ’n binneste lys moet verleen word voordat daardie kombinasie van toepassing is. Hou kombinasies bymekaar; as hulle in individuele toekennings verdeel word, sal dit die risiko oorskat. Bestaande presiese en regular-expression-velde bly die terugvalopsie vir toestemmings wat nie in die katalogus voorkom nie. ’n Volledige herskrywing van die klassifiseerder of nuwe passingsgedrag vereis steeds kodeveranderinge in die verbruikers.

## Kubernetes-lêer

`rules` is georden: die eerste passende reël wen. Elke reël het ’n unieke `id`, ’n `match`, ’n `severity`, en ’n gewone-taal-`description`. Voeg ’n meer spesifieke reël voor ’n breër een by, of verander ’n bestaande reël se ernstigheid. Behou die finale onvoorwaardelike terugvalopsie.

Passings gebruik `all`, `any`, en `not` vir samestelling, of ’n `field`, `op`, en `value`-vergelyking. Beskikbare velde is `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (kleinletter-nie-resource-URL), `non_resource_url`, `mode`, en `delegated_verb`. Bewerkings is `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, en `truthy` (geen waarde benodig nie). `always: true` pas by alles. Groep-, resource-, subresource- en verbwaardes is kleinletters. ’n Letterlike wildcard word as `'*'` geskryf; passing teen ’n wildcard-toekenning is eksplisiet in die reëls, eerder as shell-patroonuitbreiding.

`severity_when` kies opsioneel ’n ander ernstigheid vir ’n passende toestand. `severity: delegated` is gereserveer vir beperkte impersonation: sy `delegated_severities`-kaart skakel die gedelegeerde aksie se klassifikasie na die voorwaardelike gradering om. Beskrywingsplekhouers kan na die beskikbare velde verwys, soos `{full}` en `{verb}`. Die reëls is data en word nooit as Python- of shell-kode geëvalueer nie.

## Validering en sinkronisering

Voer `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` met PyYAML geïnstalleer uit voordat veranderinge ingedien word. Die boek se pull-request-werkvloei voer dieselfde validering uit.

Elke Maandag haal albei verbruikersbewaarplekke die huidige `master` van hierdie boek uit, valideer al vier lêers, vergelyk SHA-256-hashes, en werk hul gebundelde YAML-lêers en gegenereerde verouderde lyste by. ’n Bronmanifest teken die boekhersiening en elke lêer se hash aan. Onverwante veranderinge aan die boek lei tot geen verbruikerscommit nie. Elke werkvloei ondersteun ook ’n handmatige uitvoering. Toetse loop voordat die werkvloei veranderde data na die verbruiker se verstektak commit; mislukkings laat daardie tak onveranderd. Die verbruikers gebruik steeds hul gebundelde kopieë vanlyn tussen opdaterings.

Om plaaslik in ’n verbruiker by te werk, voer `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` uit. Voeg `--check` by om verouderde kopieë op te spoor sonder om hulle te skryf.
