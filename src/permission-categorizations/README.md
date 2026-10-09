# Kategorizacije rizika dozvola

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud održava zajedničke podatke o ozbiljnosti dozvola koje koriste [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Izmenite kanonsku datoteku platforme ovde, a ne generisane kopije u bilo kom od potrošača.

- **Critical**: dozvole koje direktno ili gotovo samostalno daju moćne privilegije, kreiraju identitet ili omogućavaju izvršavanje sa privilegijama.
- **High**: pristup osetljivim informacijama, akreditivima ili uslovnoj putanji za eskalaciju privilegija.
- **Medium**: DoS/prekid rada, ometanje operacija, uobičajene izmene ili uslovne mogućnosti bez dokazane putanje do osetljivih podataka ili privilegija.
- **Low**: uobičajeno otkrivanje i pristup metapodacima.

Za svaku platformu postoji po jedna kanonska YAML datoteka: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). To su mašinski čitljive datoteke; stranice platformi prikazuju njihov kompletan YAML u pregledaču i objašnjavaju kako da ih izmenite. Ugrađeni prikazivač koristi kopiju iz knjige, dok PEASS radni tokovi preuzimaju kanonske datoteke sa GitHub-a.

## Datoteke cloud provajdera

`version` i `provider` identifikuju šemu. `permission_categories` sadrži četiri pojedinačne liste dozvola. Premestite dozvolu između lista da biste promenili njenu ocenu. Uparivanje za AWS i Azure zanemaruje velika i mala slova; uparivanje za GCP razlikuje velika i mala slova. Varijante koje se razlikuju samo po velikim i malim slovima mogu se ponoviti unutar istog nivoa ozbiljnosti, ali protivrečne ocene se odbacuju.

`severity_overrides` sadrži proverene izuzetke od generičkih pravila. Ako se izuzetak pojavljuje i u katalogu, oba zapisa moraju da se podudaraju. `severity_caps` sprečava da kombinacija unapredi odabrane dozvole. `non_permission_identifiers` izuzima dokumentovane nazive API metoda, uslovne ključeve i druge nizove koji nisu stvarne autorizacione dozvole.

`combinations.critical` i `combinations.high` su liste lista dozvola: svaka stavka unutrašnje liste mora biti dodeljena da bi se ta kombinacija primenila. Držite kombinacije na okupu; njihovo razdvajanje na pojedinačne dodele precenilo bi rizik. Postojeća polja za tačno poklapanje i regularne izraze ostaju rezervna opcija za dozvole koje nisu u katalogu. Potpuno prepisivanje klasifikatora ili uvođenje novog ponašanja pri uparivanju i dalje zahteva izmene koda u potrošačima.

## Kubernetes datoteka

`rules` je uređena lista: primenjuje se prvo pravilo koje se podudara. Svako pravilo ima jedinstveni `id`, `match`, `severity` i `description` na običnom jeziku. Dodajte konkretnije pravilo pre opštijeg ili promenite ozbiljnost postojećeg pravila. Sačuvajte završno bezuslovno rezervno pravilo.

Uslovi poklapanja koriste `all`, `any` i `not` za kombinovanje, ili poređenje `field`, `op` i `value`. Dostupna polja su `group`, `resource`, `subresource`, `full` (resurs/podresurs), `verb`, `namespace`, `name`, `path` (URL koji nije resurs, malim slovima), `non_resource_url`, `mode` i `delegated_verb`. Operacije su `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (ne zahteva vrednost). `always: true` odgovara svemu. Vrednosti za grupu, resurs, podresurs i glagol pišu se malim slovima. Doslovni džoker zapisuje se kao `'*'`; poklapanje dodele sa džokerom izričito je navedeno u pravilima, umesto da se koristi proširivanje šablona ljuske.

`severity_when` opcionalno bira drugu ozbiljnost za uslov koji se podudara. `severity: delegated` rezervisano je za ograničeno predstavljanje drugog korisnika: njegova mapa `delegated_severities` pretvara klasifikaciju delegirane radnje u uslovnu ocenu. Mesta za umetanje u opis mogu da upućuju na dostupna polja, kao što su `{full}` i `{verb}`. Pravila su podaci i nikada se ne izvršavaju kao Python ili shell kod.

## Provera i sinhronizacija

Pre slanja izmena pokrenite `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` uz instaliran PyYAML. Radni tok za pull request u knjizi pokreće istu proveru.

Svakog ponedeljka, oba repozitorijuma potrošača preuzimaju aktuelni `master` ove knjige, proveravaju sve četiri datoteke, upoređuju SHA-256 heševe i ažuriraju svoje objedinjene YAML datoteke i generisane zastarele liste. Manifest izvora beleži reviziju knjige i heš svake datoteke. Nepovezane izmene knjige ne dovode do commita u repozitorijumu potrošača. Svaki radni tok podržava i ručno pokretanje. Testovi se pokreću pre nego što radni tok upiše izmenjene podatke u podrazumevanu granu potrošača; u slučaju neuspeha ta grana ostaje nepromenjena. Potrošači nastavljaju da koriste svoje objedinjene kopije van mreže između ažuriranja.

Da biste lokalno ažurirali podatke u potrošaču, pokrenite `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodajte `--check` da biste otkrili zastarele kopije bez njihovog upisivanja.

Preuzimanje izvora u oba potrošača pokušava se ponovo pet puta, uz ograničeno trajanje preuzimanja i sve duže pauze. Nepotpuna preuzimanja ostaju u privremenim direktorijumima; ako se iscrpe svi pokušaji, postojeći objedinjeni podaci ostaju neizmenjeni.
{{#include ../banners/hacktricks-training.md}}
