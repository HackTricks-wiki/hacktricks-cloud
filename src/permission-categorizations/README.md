# Kategorizacije rizika dozvola

HackTricks Cloud održava zajedničke podatke o ozbiljnosti dozvola koje koriste [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Izmenite kanonski fajl platforme ovde, umesto generisanih kopija u bilo kom od potrošača.

- **Critical**: dozvole koje direktno ili gotovo samostalno dodeljuju moćne privilegije, kreiraju identitet ili omogućavaju privilegovano izvršavanje.
- **High**: pristup osetljivim informacijama, kredencijalima ili uslovnoj putanji za eskalaciju privilegija.
- **Medium**: DoS/Break, operativni prekidi, uobičajene izmene ili uslovne mogućnosti bez dokazane putanje do osetljivih podataka ili privilegija.
- **Low**: uobičajeno otkrivanje i pristup metapodacima.

Postoji jedan kanonski YAML fajl po platformi: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). Ovo su mašinski čitljivi fajlovi; stranice platformi objašnjavaju kako da ih izmenite.

## Cloud provider files

`version` i `provider` identifikuju šemu. `permission_categories` sadrži četiri pojedinačne liste dozvola. Premestite dozvolu između lista da biste promenili njenu ocenu. AWS i Azure poređenje zanemaruje veličinu slova; GCP poređenje razlikuje veličinu slova. Aliasi veličine slova mogu da se ponavljaju unutar iste kategorije ozbiljnosti, ali konfliktne ocene se odbacuju.

`severity_overrides` sadrži proverene izuzetke od generičkih pravila. Ako se izuzetak takođe nalazi u katalogu, oba unosa moraju da se slažu. `severity_caps` sprečava kombinaciju da unapredi odabrane dozvole. `non_permission_identifiers` isključuje dokumentovane nazive API metoda, ključeve uslova i druge stringove koji nisu stvarne autorizacione dozvole.

`combinations.critical` i `combinations.high` su liste lista dozvola: svaki element unutrašnje liste mora biti dodeljen da bi se ta kombinacija primenila. Držite kombinacije zajedno; njihovo razdvajanje na pojedinačne dodeljene dozvole precenilo bi rizik. Postojeća polja za tačno podudaranje i regularne izraze ostaju rezervna opcija za dozvole koje nisu prisutne u katalogu. Potpuna izmena klasifikatora ili novo ponašanje pri poređenju i dalje zahteva izmene koda u potrošačima.

## Kubernetes file

`rules` je uređen: primenjuje se prvo pravilo koje se podudara. Svako pravilo ima jedinstveni `id`, `match`, `severity` i opis na običnom jeziku. Dodajte konkretnije pravilo pre šireg pravila ili promenite ozbiljnost postojećeg pravila. Sačuvajte završnu bezuslovnu rezervnu opciju.

Podudaranja koriste `all`, `any` i `not` za sastavljanje ili poređenje `field`, `op` i `value`. Dostupna polja su `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL koji nije resurs i napisan je malim slovima), `non_resource_url`, `mode` i `delegated_verb`. Operacije su `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (nije potrebna vrednost). `always: true` se podudara sa svime. Vrednosti za group, resource, subresource i verb pišu se malim slovima. Literalni džoker-znak zapisuje se kao `'*'`; podudaranje sa dodeljenom dozvolom koja sadrži džoker-z znak eksplicitno je navedeno u pravilima, umesto proširivanja šablona ljuske.

`severity_when` opcionalno bira drugu ozbiljnost za uslov koji se podudara. `severity: delegated` rezervisano je za ograničeno impersonation: njegova mapa `delegated_severities` pretvara klasifikaciju delegirane radnje u uslovnu ocenu. Placeholders u opisu mogu da upućuju na dostupna polja, kao što su `{full}` i `{verb}`. Pravila su podaci i nikada se ne izvršavaju kao Python ili shell kod.

## Validation and synchronization

Pokrenite `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` sa instaliranim PyYAML-om pre slanja izmena. Workflow knjige za pull request pokreće istu validaciju.

Svakog ponedeljka oba potrošačka repozitorijuma preuzimaju trenutni `master` ove knjige, proveravaju sva četiri fajla, upoređuju SHA-256 hash vrednosti i ažuriraju svoje ugrađene YAML fajlove i generisane legacy liste. Izvorni manifest beleži reviziju knjige i hash vrednost svakog fajla. Nepovezane izmene u knjizi ne proizvode commit u potrošaču. Svaki workflow podržava i ručno pokretanje. Testovi se izvršavaju pre nego što workflow commituje izmenjene podatke u podrazumevanu granu potrošača; greške ostavljaju tu granu neizmenjenom. Potrošači nastavljaju da koriste svoje ugrađene kopije van mreže između ažuriranja.

Da biste lokalno ažurirali podatke u potrošaču, pokrenite `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodajte `--check` da biste otkrili zastarele kopije bez njihovog upisivanja.
