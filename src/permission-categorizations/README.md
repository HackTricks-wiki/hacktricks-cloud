# Categorizações de risco de permissões

{{#include ../banners/hacktricks-training.md}}

O HackTricks Cloud mantém os dados compartilhados de severidade de permissões consumidos pelo [CloudPEASS](https://github.com/peass-ng/CloudPEASS) e pelo [Blue-CloudPEASS](https://github.com/peass-ng/Blue-CloudPEASS). Edite aqui o arquivo canônico da plataforma, em vez das cópias geradas em qualquer um dos consumidores.

- **Critical**: permissões que concedem diretamente, ou quase independentemente, privilégios poderosos, criam uma identidade ou permitem execução privilegiada.
- **High**: acesso a informações confidenciais, credenciais ou um caminho condicional para escalonamento de privilégios.
- **Medium**: DoS/Break, interrupção operacional, alterações comuns ou capacidades condicionais sem um caminho demonstrado para dados confidenciais ou privilégios.
- **Low**: descoberta comum e acesso a metadados.

Há um arquivo YAML canônico por plataforma: [AWS](aws.yaml), [GCP](gcp.yaml), [Azure](azure.yaml) e [Kubernetes](k8s.yaml). Esses arquivos são legíveis por máquina; as páginas das plataformas exibem o YAML completo no navegador e explicam como editá-los. O visualizador integrado usa a cópia do livro, enquanto os fluxos de trabalho do PEASS buscam os arquivos canônicos no GitHub.

## Arquivos de provedores de cloud

`version` e `provider` identificam o esquema. `permission_categories` contém as quatro listas individuais de permissões. Mova uma permissão entre listas para alterar sua classificação. A correspondência de AWS e Azure ignora diferenças entre maiúsculas e minúsculas; a de GCP diferencia maiúsculas de minúsculas. Aliases de capitalização podem se repetir dentro da mesma severidade, mas classificações conflitantes são rejeitadas.

`severity_overrides` contém exceções auditadas às regras genéricas. Se uma exceção também aparecer no catálogo, as duas entradas devem coincidir. `severity_caps` impede que uma combinação eleve a classificação de permissões selecionadas. `non_permission_identifiers` exclui nomes documentados de métodos de API, chaves de condição e outras strings que não são permissões reais de autorização.

`combinations.critical` e `combinations.high` são listas de listas de permissões: cada elemento de uma lista interna precisa ser concedido para que a combinação se aplique. Mantenha as combinações agrupadas; separá-las em concessões individuais exageraria o risco. Os campos existentes de correspondência exata e expressão regular continuam sendo a alternativa para permissões ausentes do catálogo. Uma reescrita completa do classificador ou um novo comportamento de correspondência ainda exige alterações no código dos consumidores.

## Arquivo Kubernetes

`rules` é ordenado: a primeira regra correspondente é aplicada. Cada regra tem um `id` exclusivo, um `match`, uma `severity` e uma `description` em linguagem simples. Adicione uma regra mais específica antes de uma mais abrangente ou altere a severidade de uma regra existente. Preserve a regra final incondicional de fallback.

As correspondências usam `all`, `any` e `not` para composição, ou uma comparação de `field`, `op` e `value`. Os campos disponíveis são `group`, `resource`, `subresource`, `full` (resource/subresource), `verb`, `namespace`, `name`, `path` (URL de recurso não Kubernetes em minúsculas), `non_resource_url`, `mode` e `delegated_verb`. As operações são `eq`, `ne`, `in`, `not_in`, `contains`, `prefix`, `suffix` e `truthy` (não requer valor). `always: true` corresponde a tudo. Os valores de grupo, recurso, sub-recurso e verbo são escritos em minúsculas. Um curinga literal é escrito como `'*'`; a correspondência com uma concessão curinga é explícita nas regras, em vez de usar expansão de padrões do shell.

`severity_when` seleciona opcionalmente outra severidade para uma condição correspondente. `severity: delegated` é reservado para impersonation restrita: seu mapa `delegated_severities` converte a classificação da ação delegada na classificação condicional. Os placeholders da descrição podem fazer referência aos campos disponíveis, como `{full}` e `{verb}`. As regras são dados e nunca são avaliadas como código Python ou shell.

## Validação e sincronização

Execute `python scripts/sync_hacktricks_permissions.py --book-root . --validate-only` com PyYAML instalado antes de enviar alterações. O fluxo de trabalho de pull request do livro executa a mesma validação.

Toda segunda-feira, os dois repositórios consumidores fazem checkout da versão atual de `master` deste livro, validam os quatro arquivos, comparam hashes SHA-256 e atualizam seus arquivos YAML incluídos e as listas legadas geradas. Um manifesto de origem registra a revisão do livro e o hash de cada arquivo. Alterações não relacionadas no livro não geram commits nos consumidores. Cada fluxo de trabalho também oferece suporte à execução manual. Os testes são executados antes que o fluxo de trabalho faça commit dos dados alterados no branch padrão do consumidor; falhas deixam esse branch inalterado. Os consumidores continuam usando suas cópias incluídas offline entre as atualizações.

Para atualizar localmente em um consumidor, execute `python scripts/sync_hacktricks_permissions.py --book-root /path/to/hacktricks-cloud`. Adicione `--check` para detectar cópias desatualizadas sem gravar nelas.

A busca dos arquivos de origem nos dois consumidores tenta novamente cinco vezes, com limites de tempo de checkout controlados e intervalos crescentes. Downloads incompletos permanecem em diretórios temporários; se as tentativas se esgotarem, os dados incluídos existentes permanecem inalterados.
{{#include ../banners/hacktricks-training.md}}
