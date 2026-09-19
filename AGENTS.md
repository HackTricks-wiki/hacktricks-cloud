# AGENTS.md

Orientações para agentes futuros que trabalham neste repositório.

## Contexto do repositório

Este é o repositório mdBook do HackTricks Cloud. O livro principal relacionado está localizado em:

`/Users/carlospolop/git/hacktricks`

Alterações no comportamento compartilhado de theme/search geralmente precisam ser aplicadas em ambos os repositórios.

## Contrato de carregamento do índice de Search

A UI de search personalizada está localizada em:

`theme/ht_searcher.js`

Também pode haver uma cópia gerada em:

`book/theme/ht_searcher.js`

Se a produção estiver fazendo deploy do diretório `book/` já compilado, atualize ambas as cópias ou recompile o
book antes do deployment.

A ordem de carregamento do índice de search é importante e sensível a custos:

1. Carregue todos os índices de search específicos de cada idioma e de fallback do repositório do GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Somente se todos os candidatos hospedados no GitHub falharem, use como fallback a saída do mdBook da mesma origem.

Não coloque o fallback local `/searchindex.js` antes de qualquer fallback hospedado no GitHub, como
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` de `cloud.hacktricks.wiki` em produção é caro.

Para este repositório, o fallback local esperado é:

`/searchindex.js`

O fallback do main-book para este repositório é:

`/searchindex-book.js`

Esse arquivo é apenas um fallback. A fonte primária deve continuar sendo os arquivos remotos
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` em
`HackTricks-wiki/hacktricks-searchindex`.

## Publicação do índice de Search

Os workflows que publicam índices de search comprimidos e criptografados em
`HackTricks-wiki/hacktricks-searchindex` são:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

O arquivo-fonte gerado é `book/searchindex.js`. Os nomes dos artifacts remotos publicados são:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferencial)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferencial)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

O browser loader prioriza o artifact compacto v2 e mantém o artifact `.js.gz` como
fallback legado. Ambos são payloads gzip criptografados com XOR usando a chave definida em `theme/ht_searcher.js`.

## Build e validação

Verificações locais comuns:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` falhar, verifique:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edição

- Prefira `rg` para pesquisas.
- Mantenha a saída gerada de `book/` fora dos commits, a menos que solicitado explicitamente. Correções no search loader são
uma exceção quando as páginas já compiladas precisam ser corrigidas imediatamente.
- Se alterar o comportamento compartilhado do theme, compare e atualize o arquivo correspondente em
`/Users/carlospolop/git/hacktricks`.
- Não reverta alterações locais não relacionadas.
