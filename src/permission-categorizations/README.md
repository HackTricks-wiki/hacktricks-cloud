# Categorizações de risco de permissões

O HackTricks Cloud mantém os dados compartilhados de severidade de permissões consumidos pelo [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e pelo [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edite o arquivo canônico da plataforma aqui, em vez das cópias geradas em qualquer um dos consumidores.

- **Critical**: permissões que concedem diretamente, ou quase independentemente, privilégios poderosos, criam uma identidade ou permitem execução privilegiada.
- **High**: acesso a informações confidenciais, credenciais ou um caminho condicional para escalação de privilégios.
- **Medium**: DoS/Break, interrupção operacional, alterações comuns ou capacidades condicionais sem um caminho demonstrado para dados confidenciais ou privilégios.
- **Low**: descoberta comum e acesso a metadados.

Existe um arquivo YAML canônico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Esses são arquivos legíveis por máquina; as páginas das plataformas exibem seu YAML completo no navegador e explicam como editá-los. O visualizador inline usa a cópia do livro, enquanto os workflows do PEASS obtêm os arquivos canônicos do GitHub.

## Arquivos dos provedores de Cloud

`version` e `provider` identificam o schema. `permission_categories` contém as quatro listas individuais de permissões. Mova uma permissão entre as listas para alterar sua classificação. A correspondência de AWS e Azure ignora maiúsculas e minúsculas; a correspondência de GCP preserva maiúsculas e minúsculas. Aliases de maiúsculas e minúsculas podem se repetir dentro da mesma severidade, mas classificações conflitantes são rejeitadas.

`severity_overrides` contém exceções auditadas às regras genéricas. Se uma exceção também aparecer no catálogo, ambas as entradas devem concordar. `severity_caps` impede que uma combinação atualize permissões selecionadas. `non_permission_identifiers` exclui nomes de métodos de API documentados, chaves de condição e outras strings que não são permissões de autorização reais.

`combinations.critical` e `combinations.high` são listas de listas de permissões: todos os elementos de uma lista interna devem ser concedidos para que a combinação seja aplicada. Mantenha as combinações juntas; dividi-las em concessões individuais exageraria o risco. Os campos existentes exatos e de expressão regular continuam sendo o fallback para permissões ausentes do catálogo. Uma reescrita completa do classificador ou um novo comportamento de correspondência ainda exige alterações de código nos consumidores.

## Arquivo do Kubernetes

`rules` é ordenado: a primeira regra correspondente vence. Cada regra tem um `id` exclusivo, um `match`, uma `severity` e uma `description` em linguagem simples. Adicione uma regra mais específica antes de uma mais abrangente ou altere a severidade de uma regra existente. Preserve o fallback final incondicional.

As correspondências usam `all`, `any` e `not` para composição, ou uma comparação de `field`, `op` e `value`. Os campos disponíveis são `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso não pertencente ao Cloud em minúsculas), `non_resource_url`, `mode` e `delegated_verb`. As operações são `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (nenhum valor necessário). `always: true` corresponde a tudo. Os valores de group, resource, subresource e verb são escritos em minúsculas. Um wildcard literal é escrito como `'*'`; a correspondência com uma concessão wildcard é explícita nas regras, em vez de usar expansão de padrões do shell.

`severity_when` opcionalmente seleciona outra severidade para uma condição correspondente. `severity: delegated` é reservado para impersonation restrita: seu mapa `delegated_severities` converte a classificação da ação delegada na classificação condicional. Placeholders da descrição podem referenciar os campos disponíveis, como `{full}` e `{verb}`. As regras são dados e nunca são avaliadas como código Python ou shell.

## Validação e sincronização

Execute `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` com PyYAML instalado antes de enviar as alterações. O workflow de pull request do livro executa a mesma validação.

Toda segunda-feira, ambos os repositórios consumidores fazem checkout do `master` atual deste livro, validam os quatro arquivos, comparam hashes SHA-256 e atualizam seus arquivos YAML incluídos e as listas legadas geradas. Um manifesto de origem registra a revisão do livro e o hash de cada arquivo. Alterações não relacionadas no livro não produzem nenhum commit do consumidor. Cada workflow também oferece uma execução manual. Os testes são executados antes que o workflow faça commit dos dados alterados no branch padrão do consumidor; falhas deixam esse branch inalterado. Os consumidores continuam usando suas cópias incluídas offline entre as atualizações.

Para atualizar localmente em um consumidor, execute `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Adicione `--check` para detectar cópias desatualizadas sem gravá-las.

A obtenção da origem em ambos os consumidores tenta novamente cinco vezes, com limites de tempo de checkout definidos e atrasos crescentes. Downloads incompletos permanecem em diretórios temporários; quando as tentativas se esgotam, os dados incluídos existentes permanecem inalterados.
