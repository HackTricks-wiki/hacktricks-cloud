# Caminhos de escalonamento de privilégios

{{#include ../banners/hacktricks-training.md}}

O HackTricks Cloud mantém o catálogo de escalonamento de privilégios legível por máquina consumido pelo [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Cada técnica indica quais permissões um principal precisa efetivamente ter e em quais recursos para obter os privilégios de um conjunto de principais-alvo. O Blue-CloudPEASS avalia essas entradas offline com base em um snapshot de inventário somente leitura e desenha caminhos de ataque de principal a principal, indicando como evidência a política ou o vínculo que concede o acesso e a mitigação que elimina o caminho. Edite aqui os arquivos canônicos, não as cópias no consumidor.

As entradas descrevem apenas os pré-requisitos, os alvos alcançáveis e a mitigação. Elas não contêm comandos, payloads nem etapas de execução; a página vinculada do HackTricks explica a técnica.

## Estrutura

Há um diretório por plataforma (`aws`, `gcp`, `azure`, `k8s`) e um arquivo `<service>.yaml` por serviço, cada um contendo uma lista YAML de técnicas. Os arquivos chamados `_excluded*.yaml` listam técnicas do HackTricks revisadas que intencionalmente não têm uma entrada, como pós-exploração, persistência ou técnicas que não podem ser modeladas a partir da configuração, junto com o motivo. `privesc-technique.schema.json` é o JSON Schema exportado para preenchimento automático e validação no editor.

## Campos da técnica

- `id`: identificador globalmente único, em minúsculas e kebab-case, prefixado com a plataforma.
- `provider`, `service`, `title` e `summary`: uma frase descrevendo o que a origem obtém.
- `source`: a página e a âncora do HackTricks que documentam a técnica, relativas a este livro. `source_revision` é o commit do livro consultado.
- `requires`: as permissões que a origem precisa ter. `all_of` lista todos os itens necessários, e `any_of` lista as alternativas. Os itens de AWS e GCP usam `action` e `resource`; os itens de Azure usam `action` (ou `data_action`) e `scope`; os itens de Entra ID usam `entra_permission` ou `entra_role`; e os itens de Kubernetes usam `verb`, `resource`, `subresource`, `api_group` e `namespace`. Placeholders como `{target.arn}` associam um requisito ao alvo.
- `target`: o `kind` do alvo, um `selector` cujas condições devem ser todas satisfeitas para que um principal seja alcançável, e seu `scope`.
- `conditions` e `blockers`: o que pode impedir o caminho na prática, como chaves de condição, SCPs, limites ou políticas de admissão.
- `confidence`, `severity`, `mitigation`, `references` e `notes` opcionais.

Campos, tipos de alvo, chaves de seletor e placeholders desconhecidos são rejeitados em vez de ignorados, para que uma entrada nunca possa ampliar ou restringir silenciosamente o conjunto de alvos. Primeiro, adicione suporte a um novo seletor no avaliador do consumidor.

### Junções do Schema v2

O carregador v2 adiciona dois placeholders e um seletor de AWS, além de permitir o seletor existente de pod em execução do K8s em alvos GCP. Esses campos exigem uma junção exata com o inventário coletado; a ausência de inventário resulta em cobertura desconhecida, não em um caminho alcançável.

| Campo | Uso e formato exigido |
| --- | --- |
| `{source.assumable_role_attached_policy_arn}` e `target.selector.via_assumable_role_attached_policy_covered_by: iam:CreatePolicyVersion` | Use-os juntos em um alvo AWS `aws_account_admin`. Cada alternativa de requisito deve incluir `iam:CreatePolicyVersion` nesse placeholder. A política deve estar anexada a uma role que a origem possa assumir na mesma conta; o avaliador verifica a capacidade de versões da política e recalcula as permissões efetivas da role. `SetDefaultPolicyVersion` não é coberto. |
| `target.selector.k8s_sa_used_by_running_pod: true` | Em um alvo GCP `k8s_service_account` com `scope: cluster`, seleciona KSAs usados por pods em execução com um token disponível no cluster GKE correspondente. Não combine com `k8s_sa_in_cluster` ou `k8s_sa_has_token_secret`. O uso existente em K8s não muda. |
| `{source_rolebound_clusterrole}` | Use como `resource_name` em requisitos K8s `clusterroles` com `api_group: rbac.authorization.k8s.io` e `namespace: "*"`. Cada alternativa precisa de `escalate` e `update` ou `patch` no mesmo nome. O alvo deve ser um `k8s_service_account` com `scope: same_namespace` e `selector.k8s_sa_in_namespace: "{target.namespace}"`; um RoleBinding deve vincular a origem nesse namespace. |

## Validação e sincronização

Execute `python scripts/validate_privesc_paths.py --book-root .` com PyYAML instalado antes de enviar as alterações. O comando verifica a estrutura de diretórios, cada entrada usando o carregador estrito do avaliador (`scripts/privesc_paths_schema.py`, uma cópia do módulo de schema do Blue-CloudPEASS), ids exclusivos, páginas de origem e âncoras de títulos, além de verificar se o JSON Schema está atualizado. Use `--peaso-root /path/to/Blue-CloudPEASS` para também comparar byte a byte os dois arquivos de schema com os do consumidor. O fluxo de pull request do livro executa a mesma validação.

Toda segunda-feira, o Blue-CloudPEASS faz checkout do `master` atual deste livro, valida esses arquivos e compara o hash SHA-256 de cada arquivo com os hashes registrados na sincronização anterior. Adições, atualizações e exclusões upstream substituem as cópias inalteradas do consumidor. Um arquivo alterado em ambos os lados é reportado como conflito, e ids de técnicas nunca são removidos sem um registro explícito revisado. Conteúdo inválido ou um teste com falha mantém inalterada a branch padrão do consumidor. Alterações não relacionadas no livro não geram commits no consumidor.
{{#include ../banners/hacktricks-training.md}}
