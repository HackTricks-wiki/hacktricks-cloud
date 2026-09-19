# AGENTS.md

Orientações para futuros agentes que trabalham neste repositório.

## Contexto do repositório

Este é o repositório mdBook do HackTricks Cloud. O livro principal relacionado está em:

`/Users/carlospolop/git/hacktricks`

Alterações no comportamento compartilhado de tema/pesquisa geralmente precisam ser aplicadas em ambos os repositórios.

## Contrato de carregamento do índice de pesquisa

A interface de pesquisa personalizada está em:

`theme/ht_searcher.js`

Também pode haver uma cópia gerada em:

`book/theme/ht_searcher.js`

Se a produção estiver implantando o diretório `book/` já compilado, atualize ambas as cópias ou recompile o
livro antes da implantação.

A política de origem do índice de pesquisa é importante e sensível a custos:

- Em hosts públicos, carregue todos os candidatos específicos de idioma e de fallback somente de
`HackTricks-wiki/hacktricks-searchindex`. Nunca use como fallback a saída mdBook da mesma origem;
servir o índice grande de `cloud.hacktricks.wiki` em produção é caro.
- Em localhost, hosts `.local`/`.internal`, loopback, RFC1918, NAT de nível de operadora, endereços link-local ou
endereços IPv6 privados, carregue somente a saída mdBook da mesma origem para que as implantações locais/em
contêineres permaneçam autocontidas.

Para este repositório, o fallback local esperado é:

`/searchindex.js`

O fallback do livro principal para este repositório é:

`/searchindex-book.js`

Esses arquivos locais são fontes somente para redes privadas. Hosts públicos devem usar exclusivamente os arquivos
remotos `searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` em
`HackTricks-wiki/hacktricks-searchindex`.

## Publicação do índice de pesquisa

Os workflows que publicam índices de pesquisa compactados e criptografados em
`HackTricks-wiki/hacktricks-searchindex` são:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

O arquivo-fonte gerado é `book/searchindex.js`. Os nomes dos artefatos remotos publicados são:

- `searchindex-cloud-v2-en.json.gz` (índice compacto preferencial)
- `searchindex-cloud-v2-<lang>.json.gz` (índice compacto preferencial)
- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

O carregador do navegador prioriza o artefato compacto v2 e mantém o artefato `.js.gz` como fallback legado.
Ambos são payloads gzip criptografados com XOR usando a chave definida em `theme/ht_searcher.js`.

O carregador deve permanecer lazy: a navegação normal entre páginas não deve criar o search worker nem baixar um
índice até que o visitante abra ou use a pesquisa. As respostas remotas compactadas são persistidas no Cache
Storage por 24 horas por origem, para que páginas subsequentes possam reutilizá-las. Preserve o fallback do
cache obsoleto quando a atualização de uma entrada expirada falhar.

## Compilação e validação

Verificações locais comuns:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` falhar, verifique:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de edição

- Prefira `rg` para pesquisas.
- Mantenha a saída gerada de `book/` fora dos commits, salvo solicitação explícita. Correções no search loader
são uma exceção quando as páginas já compiladas precisam ser corrigidas imediatamente.
- Se alterar o comportamento compartilhado do tema, compare e atualize o arquivo correspondente em
`/Users/carlospolop/git/hacktricks`.
- Não reverta alterações locais não relacionadas.
