# Kategorizacije rizika dozvola

HackTricks Cloud održava zajedničke podatke o nivou ozbiljnosti dozvola koje koriste [CloudPEASS](https://github.com/peass-ng/CloudPEASS) i [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Menjajte kanonski fajl platforme ovde, umesto generisanih kopija u bilo kom od korisnika.

- **Critical**: dozvole koje direktno ili gotovo nezavisno dodeljuju moćne privilegije, kreiraju identitet ili omogućavaju privilegovano izvršavanje.
- **High**: pristup osetljivim informacijama, credentialima ili uslovnoj putanji za eskalaciju privilegija.
- **Medium**: DoS/Break, operativni prekidi, uobičajene izmene ili uslovne mogućnosti bez dokazane putanje do osetljivih podataka ili privilegija.
- **Low**: uobičajeno otkrivanje i pristup metapodacima.

Postoji jedan kanonski YAML fajl po platformi: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) i [Kubernetes](k8s.yaml). Ovo su mašinski čitljivi fajlovi; stranice platformi prikazuju njihov kompletan YAML u browseru i objašnjavaju kako da ih menjate. Inline viewer koristi kopiju iz knjige, dok PEASS workflows preuzimaju kanonske fajlove sa GitHub-a.

## Fajlovi cloud provajdera

`version` i `provider` identifikuju šemu. `permission_categories` sadrži četiri pojedinačne liste dozvola. Premeštanjem dozvole između lista menjate njenu ocenu. AWS i Azure matching ignorišu veličinu slova; GCP matching čuva veličinu slova. Aliasi veličine slova mogu da se ponavljaju unutar istog nivoa ozbiljnosti, ali neusaglašene ocene se odbijaju.

`severity_overrides` sadrži proverene izuzetke od generičkih pravila. Ako se izuzetak takođe pojavljuje u katalogu, obe stavke moraju imati istu vrednost. `severity_caps` sprečava kombinaciju da unapredi odabrane dozvole. `non_permission_identifiers` isključuje dokumentovane nazive API metoda, condition keys i druge stringove koji nisu stvarne authorization dozvole.

`combinations.critical` i `combinations.high` su liste lista dozvola: svaki element unutrašnje liste mora biti dodeljen da bi se ta kombinacija primenila. Držite kombinacije zajedno; njihovo razdvajanje na pojedinačne grantove preuveličalo bi rizik. Postojeća polja za exact i regular-expression matching ostaju fallback za dozvole koje nisu prisutne u katalogu. Potpuna izmena classifier-a ili novo ponašanje matchinga i dalje zahteva izmene koda u korisnicima.

## Kubernetes fajl

`rules` je uređeno: prvo matching pravilo ima prednost. Svako pravilo ima jedinstveni `id`, `match`, `severity` i `description` na običnom jeziku. Dodajte specifičnije pravilo pre šireg ili promenite severity postojećeg pravila. Sačuvajte završni unconditional fallback.

Matches koriste `all`, `any` i `not` za kompoziciju ili poređenje pomoću `field`, `op` i `value`. Dostupna polja su `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL ka non-resource putanji pisan malim slovima), `non_resource_url`, `mode` i `delegated_verb`. Operacije su `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` i `truthy` (vrednost nije potrebna). `always: true` odgovara svemu. Vrednosti za group, resource, subresource i verb pišu se malim slovima. Literalni wildcard zapisuje se kao `'*'`; matching wildcard grant-a eksplicitno je naveden u pravilima, umesto proširivanja shell pattern-a.

`severity_when` opciono bira drugi severity za uslov koji odgovara. `severity: delegated` rezervisan je za ograničeni impersonation: njegova mapa `delegated_severities` pretvara klasifikaciju delegirane radnje u uslovnu ocenu. Placeholder-i u description-u mogu da upućuju na dostupna polja, kao što su `{full}` i `{verb}`. Pravila su podaci i nikada se ne izvršavaju kao Python ili shell kod.

## Validacija i sinhronizacija

Pre slanja izmena pokrenite `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` sa instaliranim PyYAML-om. Workflow za pull request u knjizi pokreće istu validaciju.

Svakog ponedeljka oba korisnička repozitorijuma preuzimaju trenutni `master` ove knjige, validiraju sva četiri fajla, upoređuju SHA-256 hash-eve i ažuriraju svoje bundled YAML fajlove i generisane legacy liste. Source manifest beleži reviziju knjige i hash svakog fajla. Nepovezane izmene u knjizi ne stvaraju commit u korisničkom repozitorijumu. Svaki workflow podržava i ručno pokretanje. Testovi se pokreću pre nego što workflow commituje izmenjene podatke u default branch korisnika; greške ostavljaju tu granu nepromenjenom. Korisnici nastavljaju da koriste svoje bundled kopije offline između ažuriranja.

Da biste lokalno ažurirali podatke u korisniku, pokrenite `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Dodajte `--check` da biste otkrili zastarele kopije bez njihovog upisivanja.

Preuzimanje source fajlova u oba korisnika pokušava se pet puta, uz ograničene rokove za checkout i sve duža čekanja. Nepotpuna preuzimanja ostaju u privremenim direktorijumima; nakon iscrpljivanja svih pokušaja postojeći bundled podaci ostaju nepromenjeni.
