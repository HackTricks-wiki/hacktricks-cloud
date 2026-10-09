# Uainishaji wa hatari za ruhusa

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud hudumisha data ya pamoja ya ukali wa ruhusa inayotumiwa na [CloudPEASS](https://github.com/peass-ng/CloudPEASS) na [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Hariri faili rasmi ya jukwaa hapa, badala ya nakala zilizozalishwa katika mojawapo ya hazina hizi.

- **Kali**: ruhusa zinazotoa moja kwa moja, au karibu bila kutegemea ruhusa nyingine, uwezo mkubwa, kuunda utambulisho, au kuwezesha utekelezaji wenye upendeleo.
- **Juu**: ufikiaji wa taarifa nyeti, vitambulisho, au njia ya kupandisha upendeleo yenye masharti.
- **Wastani**: DoS/Break, kuvuruga utendakazi, mabadiliko ya kawaida, au uwezo wenye masharti bila njia iliyothibitishwa ya kufikia data nyeti au kupata upendeleo.
- **Chini**: ugunduzi wa kawaida na ufikiaji wa metadata.

Kuna faili moja rasmi ya YAML kwa kila jukwaa: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml), na [Kubernetes](k8s.yaml). Hizi ni faili zinazosomeka na mashine; kurasa za majukwaa huonyesha YAML yake yote kwenye kivinjari na kueleza jinsi ya kuihariri. Kionyeshi kilichopachikwa hutumia nakala ya kitabu, huku michakato ya PEASS ikichukua faili rasmi kutoka GitHub.

## Faili za watoa huduma wa cloud

`version` na `provider` hutambulisha schema. `permission_categories` ina orodha nne za ruhusa. Hamisha ruhusa kati ya orodha ili kubadilisha ukadiriaji wake. Ulinganishaji wa AWS na Azure hauzingatii tofauti ya herufi kubwa na ndogo; ulinganishaji wa GCP huzingatia tofauti hiyo. Majina mbadala yanayotofautiana kwa herufi kubwa na ndogo yanaweza kujirudia ndani ya kiwango kilekile cha ukali, lakini ukadiriaji unaokinzana hukataliwa.

`severity_overrides` ina vighairi vilivyokaguliwa kwa kanuni za jumla. Ikiwa kighairi pia kipo kwenye katalogi, maingizo yote mawili lazima yalingane. `severity_caps` huzuia mchanganyiko usipandishe ukadiriaji wa ruhusa zilizochaguliwa. `non_permission_identifiers` huondoa majina ya mbinu za API yaliyoandikwa kwenye nyaraka, funguo za masharti, na mifuatano mingine ambayo si ruhusa halisi za uidhinishaji.

`combinations.critical` na `combinations.high` ni orodha za orodha za ruhusa: kila kipengele katika orodha ya ndani lazima kiwe kimetolewa ili mchanganyiko huo utumike. Ziache pamoja; kuzigawa kuwa ruhusa za kibinafsi kungeongeza kupita kiasi makadirio ya hatari. Sehemu zilizopo za ulinganishaji halisi na wa usemi wa kawaida bado ndizo mbadala kwa ruhusa ambazo hazipo kwenye katalogi. Uandishi upya kamili wa kiainishaji au tabia mpya ya ulinganishaji bado inahitaji mabadiliko ya msimbo katika watumiaji wa faili hizi.

## Faili ya Kubernetes

`rules` hupangwa kwa mfuatano: kanuni ya kwanza inayolingana ndiyo hutumika. Kila kanuni ina `id` ya kipekee, `match`, `severity`, na `description` iliyoandikwa kwa lugha rahisi. Ongeza kanuni mahususi zaidi kabla ya kanuni pana, au badilisha ukali wa kanuni iliyopo. Hifadhi kanuni ya mwisho ya fallback isiyo na masharti.

Ulinganishaji hutumia `all`, `any`, na `not` kuunda masharti, au ulinganisho wa `field`, `op`, na `value`. Sehemu zinazopatikana ni `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL ya rasilimali isiyo ya kawaida iliyo katika herufi ndogo), `non_resource_url`, `mode`, na `delegated_verb`. Operesheni ni `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix`, na `truthy` (haihitaji value). `always: true` hulingana na kila kitu. Thamani za group, resource, subresource, na verb huandikwa kwa herufi ndogo. Alama ya wildcard halisi huandikwa kama `'*'`; ulinganishaji wa ruhusa ya wildcard huainishwa waziwazi kwenye kanuni, badala ya kutumia upanuzi wa mifumo ya shell.

`severity_when` inaweza kuchagua ukali mwingine kwa sharti linalolingana. `severity: delegated` hutumika tu kwa uigaji wa utambulisho wenye vikwazo: ramani yake ya `delegated_severities` hubadilisha uainishaji wa kitendo kilichokabidhiwa kuwa ukadiriaji wa masharti. Vigeuzi vya maelezo vinaweza kurejelea sehemu zinazopatikana, kama vile `{full}` na `{verb}`. Kanuni hizi ni data na hazitekelezwi kama msimbo wa Python au shell.

## Uthibitishaji na usawazishaji

Endesha `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` ukiwa na PyYAML iliyosakinishwa kabla ya kuwasilisha mabadiliko. Mchakato wa maombi ya mabadiliko ya kitabu huendesha uthibitishaji huohuo.

Kila Jumatatu, hazina zote mbili zinazotumia faili hizi hukagua toleo la sasa la `master` la kitabu hiki, huthibitisha faili zote nne, hulinganisha hash za SHA-256, na kusasisha faili zao za YAML zilizojumuishwa pamoja na orodha za zamani zilizozalishwa. Faili ya manifesti ya chanzo huhifadhi marekebisho ya kitabu na hash ya kila faili. Mabadiliko yasiyohusiana kwenye kitabu hayasababishi commit kwenye hazina za watumiaji. Kila mchakato pia unaweza kuendeshwa mwenyewe. Majaribio huendeshwa kabla ya mchakato ku-commit data iliyobadilika kwenye tawi-msingi la mtumiaji; hitilafu zikijitokeza, tawi hilo hubaki bila mabadiliko. Watumiaji huendelea kutumia nakala zao zilizojumuishwa bila mtandao kati ya masasisho.

Ili kusasisha faili ndani ya hazina ya mtumiaji, endesha `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Ongeza `--check` ili kugundua nakala zilizopitwa na wakati bila kuziandika upya.

Upakuaji wa chanzo katika hazina zote mbili hujaribu mara tano, ukiwa na muda wa mwisho wa checkout wenye kikomo na vipindi vya kusubiri vinavyoongezeka. Upakuaji usiokamilika hubaki kwenye saraka za muda; majaribio yakimalizika bila mafanikio, data iliyojumuishwa tayari hubaki bila mabadiliko.
{{#include ../banners/hacktricks-training.md}}
