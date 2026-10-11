# Putevi eskalacije privilegija

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud održava mašinski čitljiv katalog eskalacije privilegija koji koristi [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Svaka tehnika navodi koje dozvole principal mora efektivno da ima i nad kojim resursima da bi dobio privilegije skupa ciljnih principala. Blue-CloudPEASS offline procenjuje ove unose na osnovu read-only inventarskog snimka i prikazuje putanje napada od principala do principala, uz politiku ili binding koji dodeljuje dozvole kao dokaz i meru za ublažavanje kojom se putanja uklanja. Menjajte kanonske datoteke ovde, a ne njihove kopije u potrošaču.

Unosi opisuju samo preduslove, dostupne ciljeve i meru za ublažavanje. Ne sadrže komande, payload-e ni korake izvršavanja; povezana HackTricks stranica objašnjava tehniku.

## Struktura

Postoji po jedan direktorijum za svaku platformu (`aws`, `gcp`, `azure`, `k8s`) i po jedna datoteka `<service>.yaml` za svaki servis, od kojih svaka sadrži YAML listu tehnika. Datoteke nazvane `_excluded*.yaml` navode pregledane HackTricks tehnike za koje namerno ne postoji unos, kao što su post-exploitation, persistence ili tehnike koje se ne mogu modelovati na osnovu konfiguracije, uz obrazloženje. `privesc-technique.schema.json` je izvezeni JSON Schema za dovršavanje unosa u editoru i validaciju.

## Polja tehnike

- `id`: globalno jedinstven, malim slovima i u kebab-case formatu, sa prefiksom platforme.
- `provider`, `service`, `title` i `summary`: jedna rečenica koja opisuje šta izvor dobija.
- `source`: HackTricks stranica i sidro koje dokumentuju tehniku, relativno u odnosu na ovu knjigu. `source_revision` je commit knjige koji je pregledan.
- `requires`: dozvole koje izvor mora da ima. `all_of` navodi sve obavezne stavke, a `any_of` navodi alternative. AWS i GCP stavke koriste `action` i `resource`, Azure stavke koriste `action` (ili `data_action`) i `scope`, Entra ID stavke koriste `entra_permission` ili `entra_role`, a Kubernetes stavke koriste `verb`, `resource`, `subresource`, `api_group` i `namespace`. Placeholder-i kao što je `{target.arn}` povezuju zahtev sa ciljem.
- `target`: ciljni `kind`, `selector` čiji svi uslovi moraju biti ispunjeni da bi principal bio dostupan, i njegov `scope`.
- `conditions` i `blockers`: faktori koji u praksi mogu da spreče putanju, kao što su ključevi uslova, SCP-ovi, granice ili admission policies.
- `confidence`, `severity`, `mitigation`, `references` i opcioni `notes`.

Nepoznata polja, vrste ciljeva, ključevi selektora i placeholder-i se odbacuju, umesto da budu zanemareni, tako da unos nikada ne može neprimetno da proširi ili suzi skup ciljeva. Najpre dodajte podršku za novi selector u evaluatoru potrošača.

## Validacija i sinhronizacija

Pre slanja izmena, pokrenite `python scripts/validate_privesc_paths.py --book-root .` uz instaliran PyYAML. Skripta proverava strukturu direktorijuma, svaki unos pomoću strogog loader-a evaluatora (`scripts/privesc_paths_schema.py`, kopije Blue-CloudPEASS schema modula), jedinstvenost ID-jeva, postojanje svake `source` stranice u ovoj knjizi i ažuriranost JSON Schema. Pull-request workflow knjige pokreće istu validaciju.

Svakог понедељка, Blue-CloudPEASS преузима тренутни `master` ове књиге, валидира ове датотеке и упоређује SHA-256 хеш сваке датотеке са хешевима забележеним при претходној синхронизацији. Узводна додавања, ажурирања и брисања замењују непромењене копије у потрошачу. Ако је датотека измењена на обе стране, пријављује се конфликт, а ID-јеви техника се никада не уклањају без изричито прегледаног регистра. Неисправан садржај или неуспешан тест остављају подразумевану грану потрошача непромењеном. Неповезане измене књиге не доводе до commit-а у потрошачу.
{{#include ../banners/hacktricks-training.md}}
