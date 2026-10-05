# Categorizações de risco de permissões

O HackTricks Cloud mantém os dados compartilhados de severidade de permissões consumidos pelo [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e pelo [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edite o arquivo canônico da plataforma aqui, em vez das cópias geradas em qualquer um dos consumidores.

- **Critical**: permissões que concedem diretamente, ou quase de forma independente, privilégios poderosos, criam uma identidade ou permitem execução privilegiada.
- **High**: acesso a informações sensíveis, credenciais ou um caminho condicional para escalada de privilégios.
- **Medium**: DoS/Break, interrupção operacional, alterações comuns ou capacidades condicionais sem um caminho demonstrado para dados sensíveis ou privilégios.
- **Low**: descoberta comum e acesso a metadados.

Existe um arquivo YAML canônico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Esses são arquivos legíveis por máquina; as páginas das plataformas explicam como editá-los.

## Arquivos dos provedores de Cloud

`version` e `provider` identificam o schema. `permission_categories` contém as quatro listas individuais de permissões. Mova uma permissão entre as listas para alterar sua classificação. A correspondência de AWS e Azure ignora maiúsculas e minúsculas; a correspondência de GCP preserva maiúsculas e minúsculas. Aliases de maiúsculas e minúsculas podem se repetir dentro da mesma severidade, mas classificações conflitantes são rejeitadas.

`severity_overrides` contém exceções auditadas às regras genéricas. Se uma exceção também aparecer no catálogo, ambas as entradas devem concordar. `severity_caps` impede que uma combinação eleve permissões selecionadas. `non_permission_identifiers` exclui nomes documentados de métodos de API, chaves de condição e outras strings que não são permissões reais de autorização.

`combinations.critical` e `combinations.high` são listas de listas de permissões: cada elemento de uma lista interna deve ser concedido para que essa combinação seja aplicada. Mantenha as combinações juntas; dividi-las em concessões individuais exageraria o risco. Os campos existentes exatos e de expressão regular continuam sendo o fallback para permissões ausentes do catálogo. Uma reescrita completa do classificador ou um novo comportamento de correspondência ainda exige alterações no código dos consumidores.

## Arquivo do Kubernetes

`rules` é ordenado: a primeira regra correspondente vence. Cada regra tem um `id` exclusivo, um `match`, uma `severity` e uma `description` em linguagem simples. Adicione uma regra mais específica antes de uma mais ampla ou altere a severidade de uma regra existente. Preserve o fallback final incondicional.

As correspondências usam `all`, `any` e `not` para composição, ou uma comparação de `field`, `op` e `value`. Os campos disponíveis são `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso não pertencente ao Cloud em minúsculas), `non_resource_url`, `mode` e `delegated_verb`. As operações são `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (nenhum valor necessário). `always: true` corresponde a tudo. Os valores de group, resource, subresource e verb estão em minúsculas. Um curinga literal é escrito como `'*'`; a correspondência com uma concessão curinga é explícita nas regras, em vez de usar expansão de padrões do shell.

`severity_when` opcionalmente seleciona outra severidade para uma condição correspondente. `severity: delegated` é reservado para impersonation restrita: seu mapa `delegated_severities` converte a classificação da ação delegada na classificação condicional. Placeholders da descrição podem referenciar os campos disponíveis, como `{full}` e `{verb}`. As regras são dados e nunca são avaliadas como código Python ou shell.

## Validação e sincronização

Execute `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` com PyYAML instalado antes de enviar as alterações. O workflow de pull request do livro executa a mesma validação.

Toda segunda-feira, os dois repositórios consumidores fazem checkout do `master` atual deste livro, validam os quatro arquivos, comparam hashes SHA-256 e atualizam seus arquivos YAML integrados e as listas legadas geradas. Um manifesto de origem registra a revisão do livro e o hash de cada arquivo. Alterações não relacionadas no livro não produzem nenhum commit no consumidor. Cada workflow também permite uma execução manual. Os testes são executados antes que o workflow faça commit dos dados alterados na branch padrão do consumidor; falhas deixam essa branch inalterada. Os consumidores continuam usando suas cópias integradas offline entre as atualizações.

Para atualizar localmente em um consumidor, execute `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Adicione `--check` para detectar cópias desatualizadas sem gravá-las.
