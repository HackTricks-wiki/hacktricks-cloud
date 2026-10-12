# Voorregverhogingspaaie

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hou die masjienleesbare katalogus van voorregverhoging by wat deur [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) gebruik word. Elke tegniek vermeld watter toestemmings ’n principal effektief moet hê, en op watter hulpbronne, om die voorregte van ’n stel teiken-principals te verkry. Blue-CloudPEASS evalueer hierdie inskrywings vanlyn teen ’n leesalleen-inventaris-kiekie en teken aanvalspaaie van principal tot principal, met die toestemmingsbeleid of binding as bewyse en die versagting wat die pad verwyder. Wysig die kanonieke lêers hier, eerder as die kopieë in die verbruiker.

Inskrywings beskryf net voorvereistes, die bereikbare teikens en die versagting. Hulle bevat geen opdragte, payloads of uitvoerstappe nie; die gekoppelde HackTricks-bladsy verduidelik die tegniek.

## Struktuur

Daar is een gids per platform (`aws`, `gcp`, `azure`, `k8s`) en een `<service>.yaml`-lêer per diens, elk met ’n YAML-lys tegnieke. Lêers met die naam `_excluded*.yaml` lys nagegane HackTricks-tegnieke wat doelbewus geen inskrywing het nie, soos post-exploitation, persistence of tegnieke wat nie vanuit konfigurasie gemodelleer kan word nie, saam met die rede. `privesc-technique.schema.json` is die uitgevoerde JSON Schema vir redigeerderaanvulling en -validering.

## Tegniekvelde

- `id`: wêreldwyd uniek, kleinletters en kebab-case, met die platform as voorvoegsel.
- `provider`, `service`, `title` en `summary`: een sin wat beskryf wat die bron verkry.
- `source`: die HackTricks-bladsy en anker wat die tegniek dokumenteer, relatief tot hierdie boek. `source_revision` is die boekcommit wat gelees is.
- `requires`: die toestemmings wat die bron moet hê. `all_of` lys elke vereiste item, en `any_of` lys alternatiewe. AWS- en GCP-items gebruik `action` en `resource`, Azure-items gebruik `action` (of `data_action`) en `scope`, Entra ID-items gebruik `entra_permission` of `entra_role`, en Kubernetes-items gebruik `verb`, `resource`, `subresource`, `api_group` en `namespace`. Plekhouers soos `{target.arn}` bind ’n vereiste aan die teiken.
- `target`: die teiken se `kind`, ’n `selector` waarvan al die voorwaardes moet geld vir ’n principal om bereikbaar te wees, en sy `scope`.
- `conditions` en `blockers`: wat die pad in die praktyk kan voorkom, soos toestandsleutels, SCPs, grense of toelatingsbeleide.
- `confidence`, `severity`, `mitigation`, `references` en opsionele `notes`.

Onbekende velde, teikentipes, `selector`-sleutels en plekhouers word verwerp eerder as geïgnoreer, sodat ’n inskrywing nooit sy teikenstel ongemerk kan verbreed of vernou nie. Voeg eers ondersteuning vir ’n nuwe `selector` by die verbruiker se evalueerder.

### Skema v2-verbindings

Die v2-laaier voeg twee plekhouers en een AWS-`selector` by, en laat die bestaande K8s-`selector` vir lopende pods op GCP-teikens toe. Hierdie velde vereis ’n presiese verbinding met die versamelde inventaris; ontbrekende inventaris lei tot onbekende dekking, nie ’n bereikbare pad nie.

| Veld | Gebruik en vereiste vorm |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` en `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Gebruik dit saam op ’n AWS-`aws_account_admin`-teiken. Elke vereiste alternatief moet `iam:CreatePolicyVersion` op daardie plekhouer insluit. Die beleid moet aangeheg wees aan ’n rol wat die bron in dieselfde rekening kan aanneem; die evalueerder kontroleer die kapasiteit vir beleidsweergawes en bereken die rol se effektiewe toestemmings weer. `SetDefaultPolicyVersion` word nie gedek nie. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Op ’n GCP-`k8s_service_account`-teiken met `scope: cluster` kies dit KSAs wat deur lopende pods gebruik word, met ’n beskikbare token in die ooreenstemmende GKE-kluster. Moenie dit met `k8s_sa_in_cluster` of `k8s_sa_has_token_secret` kombineer nie. Bestaande K8s-gebruik bly onveranderd. |
| `{source_rolebound_clusterrole}` | Gebruik dit as `resource_name` op K8s-`clusterroles`-vereistes met `api_group: rbac.authorization.k8s.io` en `namespace: "*"`. Elke alternatief benodig `escalate` en `update` of `patch` op dieselfde naam. Die teiken moet ’n `k8s_service_account` met `scope: same_namespace` en `selector.k8s_sa_in_namespace: "{target.namespace}"` wees; ’n RoleBinding moet die bron in daardie naamruimte bind. |

## Validering en sinchronisering

Voer `python scripts/validate_privesc_paths.py --book-root .` uit met PyYAML geïnstalleer voordat jy veranderinge indien. Dit kontroleer die gidsuitleg, elke inskrywing met die evalueerder se streng laaier (`scripts/privesc_paths_schema.py`, ’n kopie van die Blue-CloudPEASS-skemamodule), unieke ids, bronbladsye en opskrifankers, en of die JSON Schema op datum is. Gebruik `--peaso-root /path/to/Blue-CloudPEASS` om ook albei skemalêers byte vir byte met die verbruiker te vergelyk. Die boek se pull request-werkvloei voer dieselfde validering uit.

Elke Maandag haal Blue-CloudPEASS die huidige `master` van hierdie boek uit, valideer hierdie lêers en vergelyk elke lêer se SHA-256-hash met die hashes wat tydens die vorige sinchronisering aangeteken is. Toevoegings, opdaterings en skrappings stroomop vervang onveranderde verbruikerkopieë. ’n Lêer wat aan albei kante verander is, word as ’n konflik aangemeld, en tegniek-ids word nooit sonder ’n uitdruklik nagegane grootboek weggelaat nie. Ongeldige inhoud of ’n mislukte toets laat die verbruiker se verstektak onveranderd. Onverwante veranderinge aan die boek lei nie tot ’n verbruikerscommit nie.

{{#include ../banners/hacktricks-training.md}}
