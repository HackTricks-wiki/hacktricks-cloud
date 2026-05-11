# AGENTS.md

Orientações para agentes futuros trabalhando neste repositório.

## Contexto do Repositório

Este é o repositório mdBook do HackTrTricks Cloud. O livro principal relacionado está em:

`/Users/carlospolop/git/hacktricks`

Mudanças no tema compartilhado/comportamento de busca frequentemente precisam ser aplicadas em ambos os repositórios.

## Contrato de Carregamento do Índice de Busca

A interface de busca personalizada está em:

`theme/ht_searcher.js`

Também pode haver uma cópia gerada em:

`book/theme/ht_searcher.js`

Se a produção estiver implantando o diretório `book/` já construído, atualize ambas as cópias ou reconstrua o livro antes do deploy.

A ordem de carregamento do índice de busca é importante e sensível a custo:

1. Carregar todo índice de busca específico de idioma e fallback do repositório GitHub:
`HackTrTricks-wiki/hacktricks-searchindex`
2. Somente se todos os candidatos hospedados no GitHub falharem, fazer fallback para a saída mdBook do mesmo origin.

Não coloque o fallback local `/searchindex.js` antes de qualquer fallback hospedado no GitHub, como
`searchindex-cloud-en.js.gz`. Servir `searchindex.js` de `cloud.hacktricks.wiki` em produção é caro.

Para este repositório, o fallback local esperado é:

`/searchindex.js`

O fallback do livro principal para este repositório é:

`/searchindex-book.js`

Esse arquivo é apenas um fallback. A fonte primária deve permanecer os arquivos remotos
`searchindex-<lang>.js.gz` e `searchindex-cloud-<lang>.js.gz` em
`HackTrTricks-wiki/hacktricks-searchindex`.

## Publicação do Índice de Busca

Os workflows que publicam índices de busca comprimidos e criptografados para
`HackTrTricks-wiki/hacktricks-searchindex` são:

- `.github/workflows/build_master.yml`
- `.github/workflows/translate_all.yml`

O arquivo de origem gerado é `book/searchindex.js`. Os nomes dos artefatos remotos publicados são:

- `searchindex-cloud-en.js.gz`
- `searchindex-cloud-<lang>.js.gz`

O carregador do navegador espera os arquivos remotos `.js.gz` como payloads gzip criptografados por XOR usando a
chave definida em `theme/ht_searcher.js`.

## Build E Validação

Verificações locais comuns:

- `node --check theme/ht_searcher.js`
- `mdbook build`

Se `mdbook build` falhar, verifique:

- `hacktricks-preprocessor-error.log`
- `hacktricks-preprocessor.log`

## Notas de Edição

- Prefira `rg` para buscas.
- Mantenha a saída gerada de `book/` fora dos commits, a menos que seja explicitamente solicitado. Correções do carregador de busca são
uma exceção quando as páginas já construídas precisam ser corrigidas imediatamente.
- Se mudar comportamento compartilhado do tema, compare e atualize o arquivo correspondente em
`/Users/carlospolop/git/hacktricks`.
- Não reverta alterações locais não relacionadas.
