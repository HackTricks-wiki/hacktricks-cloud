# Caminhos de escalonamento de privilégios

{{#include ../banners/hacktricks-training.md}}

HackTricks Cloud mantém o catálogo de escalonamento de privilégios legível por máquina consumido pelo [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Cada técnica especifica quais permissões um principal precisa efetivamente possuir e em quais recursos para obter os privilégios de um conjunto de principais-alvo. O Blue-CloudPEASS avalia essas entradas offline, usando um snapshot de inventário somente leitura, e desenha caminhos de ataque entre principais, apresentando como evidência a política ou associação que concede o acesso e a mitigação que remove o caminho. Edite os arquivos canônicos aqui, em vez das cópias no consumidor.

As entradas descrevem apenas os pré-requisitos, os alvos alcançáveis e a mitigação. Elas não contêm comandos, payloads ou etapas de execução; a página HackTricks vinculada explica a técnica.

## Estrutura

Há um diretório por plataforma (`aws`, `gcp`, `azure`, `k8s`) e um arquivo `<service>.yaml` por serviço, cada um contendo uma lista YAML de técnicas. Os arquivos chamados `_excluded*.yaml` listam técnicas HackTricks analisadas que intencionalmente não têm uma entrada, como post-exploitation, persistência ou técnicas que não podem ser modeladas a partir da configuração, incluindo o motivo. `privesc-technique.schema.json` é o JSON Schema exportado para preenchimento automático e validação no editor.

## Campos da técnica

- `id`: único globalmente, em letras minúsculas e kebab-case, com o prefixo da plataforma.
- `provider`, `service`, `title` e `summary`: uma frase que descreve o que o alvo obtém.
- `source`: a página e a âncora do HackTricks que documentam a técnica, relativas a este livro. `source_revision` é o commit do livro consultado.
- `requires`: as permissões que o alvo precisa possuir. `all_of` lista todos os itens necessários, e `any_of` lista as alternativas. Os itens de AWS e GCP usam `action` e `resource`; os itens de Azure usam `action` (ou `data_action`) e `scope`; os itens de Entra ID usam `entra_permission` ou `entra_role`; e os itens de Kubernetes usam `verb`, `resource`, `subresource`, `api_group` e `namespace`. Placeholders como `{target.arn}` vinculam um requisito ao alvo.
- `target`: o `kind` do alvo, um `selector` cujas condições devem ser todas atendidas para que um principal seja alcançável, e seu `scope`.
- `conditions` e `blockers`: o que pode impedir o caminho na prática, como chaves de condição, SCPs, boundaries ou políticas de admissão.
- `confidence`, `severity`, `mitigation`, `references` e `notes` opcional.

Campos, tipos de alvo, chaves de seletor e placeholders desconhecidos são rejeitados em vez de ignorados, para que uma entrada nunca possa ampliar ou restringir silenciosamente o conjunto de alvos. Primeiro, adicione suporte a um novo seletor no avaliador do consumidor.

## Validação e sincronização

Execute `python scripts/validate_privesc_paths.py --book-root .` com PyYAML instalado antes de enviar as alterações. O script verifica a estrutura de diretórios, cada entrada usando o carregador rigoroso do avaliador (`scripts/privesc_paths_schema.py`, uma cópia do módulo de esquema do Blue-CloudPEASS), os ids exclusivos, a existência neste livro de cada página `source` e se o JSON Schema está atualizado. O workflow de pull request do livro executa a mesma validação.

Toda segunda-feira, o Blue-CloudPEASS faz checkout do `master` atual deste livro, valida esses arquivos e compara o hash SHA-256 de cada arquivo com os hashes registrados na sincronização anterior. Adições, atualizações e exclusões upstream substituem as cópias inalteradas no consumidor. Um arquivo alterado em ambos os lados é reportado como conflito, e ids de técnicas nunca são removidos sem um registro explícito revisado. Conteúdo inválido ou uma falha nos testes mantém inalterada a branch padrão do consumidor. Alterações não relacionadas no livro não geram commits no consumidor.
{{#include ../banners/hacktricks-training.md}}
