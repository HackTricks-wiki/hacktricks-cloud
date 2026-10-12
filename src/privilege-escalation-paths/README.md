# Putevi eskalacije privilegija

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud održava mašinski čitljiv katalog eskalacije privilegija koji koristi [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Svaka tehnika navodi koje dozvole principal mora efektivno da poseduje i nad kojim resursima da bi dobio privilegije skupa ciljnih principala. Blue-CloudPEASS van mreže procenjuje ove unose na osnovu snimka inventara koji se može samo čitati i crta puteve napada od principala do principala, uz politiku ili binding koji daje dozvolu kao dokaz i meru za ublažavanje koja uklanja put. Izmenite kanonske datoteke ovde, a ne kopije u projektu koji ih koristi.

Unosi opisuju samo preduslove, dostupne ciljeve i meru za ublažavanje. Ne sadrže komande, payload-e niti korake izvršavanja; povezana stranica HackTricks objašnjava tehniku.

## Struktura

Za svaku platformu postoji po jedan direktorijum (`aws`, `gcp`, `azure`, `k8s`), a za svaku uslugu po jedna datoteka `<service>.yaml`, od kojih svaka sadrži YAML listu tehnika. Datoteke čija imena počinju sa `_excluded` navode pregledane HackTricks tehnike koje namerno nemaju unos, na primer post-exploitation, persistence ili tehnike koje se ne mogu modelovati iz konfiguracije, uz obrazloženje. `privesc-technique.schema.json` je izvezeni JSON Schema za dopunjavanje u editoru i validaciju.

## Polja tehnike

- `id`: globalno jedinstven ID, malim slovima i u kebab-case formatu, sa prefiksom platforme.
- `provider`, `service`, `title` i `summary`: jedna rečenica koja opisuje šta izvor dobija.
- `source`: HackTricks stranica i anchor koji dokumentuju tehniku, relativno u odnosu na ovu knjigu. `source_revision` je commit knjige koji je pregledan.
- `requires`: dozvole koje izvor mora da poseduje. `all_of` navodi sve obavezne stavke, a `any_of` alternative. AWS i GCP stavke koriste `action` i `resource`, Azure stavke koriste `action` (ili `data_action`) i `scope`, Entra ID stavke koriste `entra_permission` ili `entra_role`, a Kubernetes stavke koriste `verb`, `resource`, `subresource`, `api_group` i `namespace`. Vrednosti poput `{target.arn}` vezuju zahtev za cilj.
- `target`: cilj `kind`, `selector` čiji svi uslovi moraju biti ispunjeni da bi principal bio dostupan, i njegov `scope`.
- `conditions` i `blockers`: šta u praksi može da spreči put, kao što su ključevi uslova, SCP-ovi, granice ili admission policies.
- `confidence`, `severity`, `mitigation`, `references` i opciono `notes`.

Nepoznata polja, vrste ciljeva, ključevi selektora i vrednosti placeholdera se odbacuju umesto da budu ignorisani, tako da unos nikada ne može neprimetno da proširi ili suzi skup ciljeva. Podršku za novi selektor prvo dodajte u evaluatoru koji koristi potrošač.

### Spajanja u šemi v2

Loader v2 dodaje dva placeholdera i jedan AWS selektor, a postojeći K8s selektor za podove koji su pokrenuti dozvoljava i na GCP ciljevima. Ova polja zahtevaju tačno spajanje sa prikupljenim inventarom; ako inventar nedostaje, pokrivenost je nepoznata, a ne putanja koja je dostupna.

| Polje | Namena i obavezni oblik |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` i `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Koristite zajedno na AWS cilju `aws_account_admin`. Svaka alternativa zahteva mora da sadrži `iam:CreatePolicyVersion` nad tim placeholderom. Politika mora biti pridružena ulozi koju izvor može da preuzme u istom nalogu; evaluator proverava kapacitet verzija politike i ponovo izračunava efektivne dozvole uloge. `SetDefaultPolicyVersion` nije obuhvaćen. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Na GCP cilju `k8s_service_account` sa `scope: cluster`, bira KSA-ove koje koriste pokrenuti podovi sa dostupnim tokenom u odgovarajućem GKE klasteru. Nemojte ga kombinovati sa `k8s_sa_in_cluster` ili `k8s_sa_has_token_secret`. Postojeća upotreba na K8s-u ostaje nepromenjena. |
| `{source_rolebound_clusterrole}` | Koristite kao `resource_name` u K8s zahtevima za `clusterroles` sa `api_group: rbac.authorization.k8s.io` i `namespace: "*"`. Svaka alternativa zahteva `escalate` i `update` ili `patch` nad istim imenom. Cilj mora biti `k8s_service_account` sa `scope: same_namespace` i `selector.k8s_sa_in_namespace: "{target.namespace}"`; RoleBinding mora da veže izvor u tom namespace-u. |

## Validacija i sinhronizacija

Pre slanja izmena pokrenite `python scripts/validate_privesc_paths.py --book-root .` uz instaliran PyYAML. Skripta proverava strukturu direktorijuma, svaki unos pomoću strogog loadera evaluatora (`scripts/privesc_paths_schema.py`, kopije modula šeme iz Blue-CloudPEASS), jedinstvenost ID-jeva, izvorne stranice i anchor-e naslova, kao i da li je JSON Schema aktuelna. Upotrebite `--peaso-root /path/to/Blue-CloudPEASS` da biste uporedili obe datoteke šeme sa onima u projektu koji ih koristi, bajt po bajt. Workflow za pull request u ovoj knjizi pokreće istu validaciju.

Svakog ponedeljka Blue-CloudPEASS preuzima aktuelni `master` ove knjige, validira ove datoteke i upoređuje SHA-256 hash svake datoteke sa hash vrednostima zabeleženim pri prethodnoj sinhronizaciji. Dodaci, izmene i brisanja u izvornoj knjizi zamenjuju neizmenjene kopije у projektu koji их koristi. Datoteka измењена са обе стране пријављује се као конфликт, а ID-јеви техника се никада не уклањају без изричито прегледаног регистра. Неисправан садржај или неуспешан тест оставља подразумевану грану пројекта који их користи непромењеном. Неповезане измене у књизи не доводе до commit-а у том пројекту.
{{#include ../banners/hacktricks-training.md}}
