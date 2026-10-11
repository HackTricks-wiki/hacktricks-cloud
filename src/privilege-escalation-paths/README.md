# Paaie vir voorregte-eskalasie

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hou die masjienleesbare katalogus vir voorregte-eskalasie by wat deur [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) gebruik word. Elke tegniek spesifiseer watter toestemmings ’n principal effektief moet hê, en op watter hulpbronne, om die voorregte van ’n stel teiken-principals te verkry. Blue-CloudPEASS evalueer hierdie inskrywings vanlyn teen ’n leesalleen-inventarisopname en teken aanvalspaaie van principal tot principal, met die toestemmingsverlenende beleid of binding as bewyse en die versagting wat die pad verwyder. Wysig die kanonieke lêers hier, eerder as die kopieë in die verbruiker.

Inskrywings beskryf slegs voorvereistes, die bereikbare teikens en die versagting. Hulle bevat geen opdragte, payloads of uitvoeringstappe nie; die gekoppelde HackTricks-bladsy verduidelik die tegniek.

## Uitleg

Daar is een gids per platform (`aws`, `gcp`, `azure`, `k8s`) en een `<service>.yaml`-lêer per diens, wat elk ’n YAML-lys van tegnieke bevat. Lêers met die naam `_excluded*.yaml` lys HackTricks-tegnieke wat nagegaan is en doelbewus geen inskrywing het nie, soos post-exploitation, persistence of tegnieke wat nie uit konfigurasie gemodelleer kan word nie, saam met die rede. `privesc-technique.schema.json` is die uitgevoerde JSON Schema vir redigeerderaanvulling en validering.

## Tegniekvelde

- `id`: wêreldwyd uniek, in kleinletters en kebab-case, met die platform as voorvoegsel.
- `provider`, `service`, `title` en `summary`: een sin wat beskryf wat die bron verkry.
- `source`: die HackTricks-bladsy en anker wat die tegniek dokumenteer, relatief tot hierdie boek. `source_revision` is die boek-commit wat gelees is.
- `requires`: die toestemmings wat die bron moet hê. `all_of` lys elke vereiste item, en `any_of` lys alternatiewe. AWS- en GCP-items gebruik `action` en `resource`, Azure-items gebruik `action` (of `data_action`) en `scope`, Entra ID-items gebruik `entra_permission` of `entra_role`, en Kubernetes-items gebruik `verb`, `resource`, `subresource`, `api_group` en `namespace`. Plekhouers soos `{target.arn}` koppel ’n vereiste aan die teiken.
- `target`: die teiken se `kind`, ’n `selector` waarvan al die voorwaardes moet geld sodat ’n principal bereikbaar is, en sy `scope`.
- `conditions` en `blockers`: wat die pad in die praktyk kan verhinder, soos voorwaardesleutels, SCPs, grense of toelatingsbeleide.
- `confidence`, `severity`, `mitigation`, `references` en opsionele `notes`.

Onbekende velde, teikentipes, selektorsleutels en plekhouers word verwerp eerder as geïgnoreer, sodat ’n inskrywing nooit ongemerk sy teikengroep kan verbreed of vernou nie. Voeg eers ondersteuning vir ’n nuwe selector by die verbruiker se evalueerder.

## Validering en sinchronisering

Voer `python scripts/validate_privesc_paths.py --book-root .` uit met PyYAML geïnstalleer voordat jy veranderinge indien. Dit kontroleer die gidsuitleg, elke inskrywing met die evalueerder se streng laaier (`scripts/privesc_paths_schema.py`, ’n kopie van die Blue-CloudPEASS-skemamodule), unieke ids, of elke `source`-bladsy in hierdie boek bestaan, en of die JSON Schema op datum is. Die boek se pull request-werkvloei voer dieselfde validering uit.

Elke Maandag haal Blue-CloudPEASS die huidige `master` van hierdie boek uit, valideer hierdie lêers en vergelyk elke lêer se SHA-256-hash met die hashes wat tydens die vorige sinchronisering aangeteken is. Bydraes, opdaterings en skrappings stroomop vervang onveranderde kopieë in die verbruiker. ’n Lêer wat aan albei kante verander het, word as ’n konflik aangemeld, en tegniek-ids word nooit verwyder sonder ’n ledger wat uitdruklik nagegaan is nie. Ongeldige inhoud of ’n mislukte toets laat die verbruiker se verstektak onveranderd. Onverwante veranderinge aan die boek lei nie tot ’n commit in die verbruiker nie.
{{#include ../banners/hacktricks-training.md}}
