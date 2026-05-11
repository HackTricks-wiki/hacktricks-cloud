# AGENTS.md

Guidance pour les agents futurs travaillant dans ce dépôt.

## Contexte du dépôt

Ceci est le dépôt mdBook HackTricks Cloud. Le livre principal associé se trouve à :

`/Users/carlospolop/git/hacktricks`

Les changements concernant le thème partagé/le comportement de recherche doivent souvent être appliqués dans les deux dépôts.

## Contrat de chargement de l'index de recherche

L'interface de recherche personnalisée se trouve dans :

`theme/ht_searcher.js`

Il peut aussi exister une copie générée dans :

`book/theme/ht_searcher.js`

Si le déploiement de production utilise le répertoire `book/` déjà construit, mettez à jour les deux copies ou reconstruisez le livre avant le déploiement.

L'ordre de chargement de l'index de recherche est important et sensible au coût :

1. Charger chaque index de recherche spécifique à la langue et de secours depuis le dépôt GitHub :
`HackTricks-wiki/hacktricks-searchindex`
2. Ce n'est que si tous les candidats hébergés sur GitHub échouent qu'il faut revenir à la sortie mdBook du même origine.

Ne placez pas le fallback local `/searchindex.js` avant un fallback hébergé sur GitHub tel que
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` depuis `cloud.hacktricks.wiki` en production est coûteux.

Pour ce dépôt, le fallback local attendu est :

`/searchindex.js`

Le fallback du livre principal pour ce dépôt est :

`/searchindex-book.js`

Ce fichier n'est qu'un fallback. La source primaire doit rester les fichiers distants
`searchindex-<lang>.js.gz` et `searchindex-cloud-<lang>.js.gz` dans
`HackTricks-wiki/hacktricks-searchindex`.

## Publication de l'index de recherche

Les workflows qui publient des index de recherche compressés chiffrés vers
`HackTricks-wiki/hacktricks-searchindex` sont :

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Le fichier source généré est `book/searchindex.js`. Les noms des artefacts distants publiés sont :

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Le chargeur côté navigateur attend des fichiers distants `.js.gz` qui sont des charges utiles gzip chiffrées par XOR utilisant la
clé définie dans `theme/ht_searcher.js`.

## Build et validation

Vérifications locales courantes :

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` échoue, vérifiez :

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notes d'édition

- Préférez `rg` pour rechercher.
- Gardez la sortie générée `book/` hors des commits sauf demande explicite. Les corrections du chargeur de recherche sont
une exception lorsque les pages déjà construites doivent être corrigées immédiatement.
- Si vous modifiez le comportement du thème partagé, comparez et mettez à jour le fichier correspondant dans
`/Users/carlospolop/git/hacktricks`.
- Ne rétablissez pas des modifications locales non liées.
