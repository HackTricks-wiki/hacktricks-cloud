# AGENTS.md

Orientações para futuros agentes que trabalharem neste repositório.

## Contexto do repositório

Este é o repositório mdBook do HackTricks Cloud. O livro principal relacionado está em:

`/Users/carlospolop/git/hacktricks`

Alterações no comportamento compartilhado do tema/pesquisa geralmente precisam ser aplicadas em ambos os repositórios.

## Contrato de carregamento do índice de pesquisa

A interface de pesquisa personalizada está em:

`theme/ht_searcher.js`

Também pode haver uma cópia gerada em:

`book/theme/ht_searcher.js`

Se a produção estiver fazendo deploy do diretório `book/` já compilado, atualize ambas as cópias ou compile o livro novamente.

A ordem de carregamento do índice de pesquisa é importante e sensível a custos:

1. Carregue todos os índices de pesquisa específicos de idioma e de fallback a partir do repositório do GitHub:
`HackTricks-wiki/hacktricks-searchindex`
2. Somente se todos os candidatos hospedados no GitHub falharem, faça fallback para a saída mdBook da mesma origem.

Não coloque o fallback local `/searchindex.js` antes de qualquer fallback hospedado no GitHub, como `searchindex-cloud-en.js.gz`. Servir `searchindex.js` a partir de `cloud.hacktricks.wiki` em produção é caro.

Para este repositório, o fallback local esperado é:

`/searchindex.js`

O fallback do livro principal para este repositório é:

`/searchindex-book.js`

Esse arquivo é apenas um fallback. A fonte primária deve continuar sendo os arquivos remotos
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` em
`HackTricks-wiki/hacktricks-searchindex`.

## Publicação do índice de pesquisa

Os workflows que publicam índices de pesquisa comprimidos e criptografados em
`HackTricks-wiki/hacktricks-searchindex` são:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

O arquivo-fonte gerado é `book/searchindex.js`. Os nomes dos artefatos remotos publicados são:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferencial)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferencial)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

O loader do navegador prioriza o artefato compacto v2 e mantém o artefato `.js.gz` como
fallback legado. Ambos são payloads gzip criptografados com XOR usando a chave definida em
`theme/ht_searcher.js`.

O loader deve continuar lazy: a navegação normal pelas páginas não deve criar o search worker nem baixar um índice até que o visitante abra ou use a pesquisa. As respostas remotas comprimidas são persistidas no Cache
Storage por 24 horas por origem, para que as páginas subsequentes possam reutilizá-las. Preserve o fallback para cache obsoleto ao atualizar uma entrada expirada caso a atualização falhe.

## Compilação e validação

Verificações locais comuns:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` falhar, verifique:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Observações sobre edição

- Prefira `rg` para pesquisas.
- Mantenha a saída gerada em `book/` fora dos commits, salvo quando solicitado explicitamente. Correções no search loader são uma exceção quando as páginas já compiladas precisam ser corrigidas imediatamente.
- Se alterar o comportamento compartilhado do tema, compare e atualize o arquivo correspondente em
`/Users/carlospolop/git/hacktricks`.
- Não reverta alterações locais não relacionadas.
