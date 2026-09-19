# AGENTS.md

Instructions pour les futurs agents travaillant dans ce repository.

## Contexte du repository

Il s'agit du repository HackTricks Cloud mdBook. Le livre principal associé se trouve dans :

`/Users/carlospolop/git/hacktricks`

Les modifications du comportement partagé du thème/de la recherche doivent souvent être appliquées dans les deux repositories.

## Contrat de chargement de l'index de recherche

L'interface de recherche personnalisée se trouve dans :

`theme/ht_searcher.js`

Il peut également exister une copie générée dans :

`book/theme/ht_searcher.js`

Si la production déploie le répertoire `book/` déjà compilé, mettez à jour les deux copies ou recompilez le
book avant le déploiement.

L'ordre de chargement de l'index de recherche est important et sensible aux coûts :

1. Chargez tous les index de recherche spécifiques aux langues ainsi que l'index de repli depuis le repository GitHub :
`HackTricks-wiki/hacktricks-searchindex`
2. Ce n'est que si tous les candidats hébergés sur GitHub échouent qu'il faut utiliser en dernier recours la sortie mdBook de la même origine.

Ne placez pas le repli local `/searchindex.js` avant un repli hébergé sur GitHub tel que
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` depuis `cloud.hacktricks.wiki` en production est coûteux.

Pour ce repo, le repli local attendu est :

`/searchindex.js`

Le repli du livre principal pour ce repo est :

`/searchindex-book.js`

Ce fichier est uniquement un repli. La source principale doit rester les fichiers distants
`searchindex-<lang>.js.gz` et `searchindex-cloud-<lang>.js.gz` dans
`HackTricks-wiki/hacktricks-searchindex`.

## Publication de l'index de recherche

Les workflows qui publient les index de recherche compressés et chiffrés dans `HackTricks-wiki/hacktricks-searchindex` sont :

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

Le fichier source généré est `book/searchindex.js`. Les noms des artifacts distants publiés sont :

- `searchindex-cloud-v2-en.json.gz` (index compact préféré)
- `searchindex-cloud-v2-<lang>.json.gz` (index compact préféré)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

Le browser loader privilégie l'artifact compact v2 et conserve l'artifact `.js.gz` comme
repli legacy. Les deux sont des payloads gzip chiffrés avec XOR utilisant la clé définie dans `theme/ht_searcher.js`.

Le loader doit rester lazy : la navigation normale entre les pages ne doit pas créer le search worker ni télécharger un
index tant que le visiteur n'a pas ouvert ou utilisé la recherche. Les réponses distantes compressées sont conservées dans le Cache
Storage pendant 24 heures par origine afin que les pages suivantes puissent les réutiliser. Conservez le
repli du cache obsolète lorsqu'une actualisation d'une entrée expirée échoue.

## Compilation et validation

Vérifications locales courantes :

- `node --check theme/ht_searcher.js`
- `mdbook build`

Si `mdbook build` échoue, vérifiez :

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notes d'édition

- Préférez `rg` pour effectuer des recherches.
- Évitez de versionner la sortie générée `book/` sauf demande explicite. Les corrections du search loader
font exception lorsque les pages déjà compilées doivent être corrigées immédiatement.
- Si vous modifiez le comportement partagé du thème, comparez et mettez à jour le fichier correspondant dans
`/Users/carlospolop/git/hacktricks`.
- N'annulez pas les modifications locales sans rapport.
