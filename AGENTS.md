# AGENTS.md

Conseils pour les futurs agents travaillant dans ce repository.

## Contexte du repository

Il s’agit du repository HackTricks Cloud mdBook. Le livre principal associé se trouve à l’emplacement :

`/Users/carlospolop/git/hacktricks`

Les modifications du comportement partagé du thème/de la recherche doivent souvent être appliquées dans les deux repositories.

## Contrat de chargement de l’index de recherche

L’interface de recherche personnalisée se trouve dans :

`theme/ht_searcher.js`

Une copie générée peut également se trouver à l’emplacement :

`book/theme/ht_searcher.js`

Si la production déploie le répertoire `book/` déjà compilé, mettez à jour les deux copies ou recompilez le
book avant le déploiement.

La policy concernant la source de l’index de recherche est importante et sensible aux coûts :

- Sur les hosts publics, chargez chaque candidat spécifique à une langue et de fallback uniquement depuis
`HackTricks-wiki/hacktricks-searchindex`. Ne faites jamais de fallback vers la sortie mdBook du même origin ;
la diffusion du large index depuis `cloud.hacktricks.wiki` en production est coûteuse.
- Sur localhost, les hosts `.local`/`.internal`, les adresses loopback, RFC1918, Carrier-Grade NAT, link-local ou
les adresses IPv6 privées, chargez uniquement la sortie mdBook du même origin afin que les déploiements
locaux/conteneurisés restent autonomes.

Pour ce repo, le fallback local attendu est :

`/searchindex.js`

Le fallback du livre principal pour ce repo est :

`/searchindex-book.js`

Ces fichiers locaux sont des sources réservées aux réseaux privés. Les hosts publics doivent utiliser exclusivement
les fichiers distants `searchindex-<lang>.js.gz` et `searchindex-cloud-<lang>.js.gz` dans
`HackTricks-wiki/hacktricks-searchindex`.

## Publication de l’index de recherche

Les workflows qui publient les index de recherche compressés et chiffrés vers
`HackTricks-wiki/hacktricks-searchindex` sont :

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Le fichier source généré est `book/searchindex.js`. Les noms des artifacts distants publiés sont :

- `searchindex-cloud-v2-en.json.gz` (compact index préféré)
- `searchindex-cloud-v2-<lang>.json.gz` (compact index préféré)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Le browser loader privilégie l’artifact compact v2 et conserve l’artifact `.js.gz` comme fallback legacy.
Les deux sont des payloads gzip chiffrés avec XOR utilisant la clé définie dans `theme/ht_searcher.js`.

Le loader doit rester lazy : la navigation normale entre les pages ne doit pas créer le search worker ni télécharger un index
tant que le visiteur n’a pas ouvert ou utilisé la recherche. Les réponses distantes compressées sont conservées dans le Cache
Storage pendant 24 heures par origin afin que les pages suivantes puissent les réutiliser. Préservez le fallback vers le
cache obsolète lorsqu’une actualisation d’une entrée expirée échoue.

## Build et validation

Vérifications locales courantes :

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` échoue, consultez :

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notes d’édition

- Préférez `rg` pour les recherches.
- Gardez la sortie `book/` générée hors des commits, sauf demande explicite. Les corrections du search loader
font exception lorsque les pages déjà compilées doivent être corrigées immédiatement.
- En cas de modification du comportement partagé du thème, comparez et mettez à jour le fichier correspondant dans
`/Users/carlospolop/git/hacktricks`.
- N’annulez pas les modifications locales sans rapport.
