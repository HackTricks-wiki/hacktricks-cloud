# Permission risk categorizations

HackTricks Cloud onderhou die gedeelde permission-severiteitsdata wat deur [CloudPEASS](https://github.com/peass-ng/CloudPEASS) en [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS) gebruik word. Wysig die kanonieke platformlêer hier, eerder as die gegenereerde kopieë in enige van die consumers.

- **Critical**: permissions wat direk, of byna onafhanklik, kragtige privileges verleen, ’n identity skep, of privileged execution moontlik maak.
- **High**: toegang tot sensitiewe inligting, credentials, of ’n voorwaardelike privilege escalation-pad.
- **Medium**: DoS/Break, operasionele ontwrigting, gewone veranderinge, of voorwaardelike capabilities sonder ’n gedemonstreerde sensitiewe-data- of privilege-pad.
- **Low**: gewone discovery en metadata-toegang.

Daar is een kanonieke YAML-lêer per platform: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), en [Kubernetes](k8s.yaml). Dit is masjienleesbare lêers; die platformbladsye vertoon hul volledige YAML in die browser en verduidelik hoe om dit te wysig. Die inline viewer gebruik die book se kopie, terwyl die PEASS-workflows die kanonieke lêers vanaf GitHub haal.

## Cloud provider files

`version` en `provider` identifiseer die schema. `permission_categories` bevat die vier individuele permission-lyste. Skuif ’n permission tussen lyste om sy rating te verander. AWS- en Azure-matching ignoreer hoofletters; GCP-matching behou hooflettergevoeligheid. Case aliases kan binne dieselfde severity herhaal word, maar teenstrydige ratings word verwerp.

`severity_overrides` bevat geouditeerde uitsonderings op generiese reëls. Indien ’n uitsondering ook in die catalog voorkom, moet albei inskrywings ooreenstem. `severity_caps` verhoed dat ’n kombinasie geselekteerde permissions opgradeer. `non_permission_identifiers` sluit gedokumenteerde API-method-name, condition keys, en ander stringe uit wat nie werklike authorization permissions is nie.

`combinations.critical` en `combinations.high` is lyste van permission-lyste: elke element van ’n binneste lys moet toegestaan word voordat daardie kombinasie van toepassing is. Hou kombinasies saam; om dit in individuele grants op te deel, sal die risk oorskat. Bestaande exact- en regular-expression-velde bly die fallback vir permissions wat nie in die catalog voorkom nie. ’n Volledige classifier rewrite of nuwe matching behavior vereis steeds code changes in die consumers.

## Kubernetes file

`rules` is georden: die eerste matching rule wen. Elke rule het ’n unieke `id`, ’n `match`, ’n `severity`, en ’n beskrywing in gewone taal. Voeg ’n meer spesifieke rule voor ’n breër een by, of verander ’n bestaande rule se severity. Behou die finale onvoorwaardelike fallback.

Matches gebruik `all`, `any`, en `not` vir samestelling, of ’n `field`, `op`, en `value`-vergelyking. Beskikbare velde is `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (kleinletters non-resource URL), `non_resource_url`, `mode`, en `delegated_verb`. Bewerkings is `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, en `truthy` (geen value benodig nie). `always: true` match alles. Group-, resource-, subresource-, en verb-values is kleinletters. ’n Letterlike wildcard word as `'*'` geskryf; matching van ’n wildcard grant word eksplisiet in die rules aangedui, eerder as shell pattern expansion.

`severity_when` kies opsioneel ’n ander severity vir ’n matching condition. `severity: delegated` is gereserveer vir beperkte impersonation: sy `delegated_severities`-map omskep die delegated action se classification in die conditional rating. Description-placeholders kan na die beskikbare velde verwys, soos `{full}` en `{verb}`. Die rules is data en word nooit as Python- of shell-code geëvalueer nie.

## Validation and synchronization

Voer `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` met PyYAML geïnstalleer uit voordat changes ingedien word. Die book se pull-request workflow voer dieselfde validation uit.

Elke Maandag check albei consumer repositories die huidige `master` van hierdie book uit, valideer al vier lêers, vergelyk SHA-256-hashes, en werk hul gebundelde YAML-lêers en gegenereerde legacy-lists op. ’n Source manifest teken die book-revisie en elke lêer se hash aan. Onverwante changes aan die book veroorsaak geen consumer commit nie. Elke workflow ondersteun ook ’n manual run. Tests loop voordat die workflow veranderde data na die consumer se default branch commit; failures laat daardie branch onveranderd. Die consumers hou aan om hul gebundelde kopieë offline tussen updates te gebruik.

Om plaaslik in ’n consumer op te dateer, voer `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud` uit. Voeg `--check` by om stale copies op te spoor sonder om dit te skryf.

Source fetching in albei consumers probeer vyf keer weer, met begrensde checkout-deadlines en toenemende vertragings. Onvolledige downloads bly in temporary directories; uitgeputte retries laat die bestaande gebundelde data onveranderd.
