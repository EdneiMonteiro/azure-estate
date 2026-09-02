# Azure Estate

[![ORCID](https://img.shields.io/badge/ORCID-0009--0006--0765--4201-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0006-0765-4201)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4?logo=microsoftazure&logoColor=white)](#)
[![Last commit](https://img.shields.io/github/last-commit/EdneiMonteiro/azure-estate)](https://github.com/EdneiMonteiro/azure-estate/commits)

## Visão Geral

Este repositório contém código de exemplo / prova de conceito (PoC) com o objetivo
de demonstrar como inventariar todo o *estate* de recursos do Azure via **Azure
Resource Graph** e gerar relatórios em **Excel e CSV** (assinaturas, grupos de
recursos, tipos de recurso e detalhes de recursos), utilizando Python e Azure
Identity.

Este projeto foi criado para fins de aprendizado, avaliação e experimentação.

## Aviso Importante

Este repositório contém **código de exemplo e não é destinado para uso em produção**.

Antes de utilizar qualquer parte deste projeto em um ambiente produtivo ou crítico,
é essencial revisar, validar, proteger e adaptar o código conforme os requisitos da
sua organização, incluindo:

- Segurança
- Escalabilidade
- Confiabilidade
- Monitoramento
- Observabilidade
- Custos
- Conformidade

Leia também:

- [DISCLAIMER.md](./DISCLAIMER.md)
- [SUPPORT.md](./SUPPORT.md)

## O que este exemplo demonstra

- Coleta de recursos via Azure Resource Graph (`azure_estate/collectors/`)
- Enriquecimento com dados que o Resource Graph não fornece
  (`azure_estate/enrich.py`): catálogo de SKUs de computação e cota restante
  via ARM (`collectors/compute_skus.py`), IP privado/sub-rede/VNet/NSG e IP
  público resolvidos pelas interfaces de rede (`collectors/network_map.py`) e
  aposentadorias de serviço anunciadas no Advisor (`collectors/retirements.py`)
- Seleção de colunas por tipo de recurso derivada do
  [microsoft/ARI](https://github.com/microsoft/ARI) (`azure_estate/ari_specs.py`,
  arquivo **gerado** — regenere com `python tools/generate_ari_configs.py`)
- Autenticação com `azure-identity`: usuário logado no Azure CLI, identidade
  gerenciada da VM ou `DefaultAzureCredential` (`azure_estate/auth.py`), com
  cache de token compartilhado entre threads
- Exportação para Excel com `openpyxl`/`pandas` e para CSV com `pandas`
  (`azure_estate/exporters/`)
- Envio dos relatórios para Azure Storage via Microsoft Entra ID: container de
  Blob (`azure_estate/exporters/blob.py`) ou File Share — este último também
  aceita chave de conta obtida por ARM (`azure_estate/exporters/file_share.py`)
- Execução agendada no Windows sem usuário logado, usando a identidade
  gerenciada da VM (`scripts/`)
- Relatórios extensíveis por registro (`azure_estate/reports/`):
  - `subscriptions` — assinaturas
  - `resource_groups` — grupos de recursos
  - `resource_types` — tipos de recurso
  - `resource_details` — detalhes de recursos

## Pré-requisitos

- Python 3.10+
- Azure CLI instalado e autenticado (`az login`) para uso interativo — a coleta
  usa a identidade do usuário logado (`AzureCliCredential`). Em execução
  agendada numa VM do Azure, use a identidade gerenciada (veja
  [Execução recorrente no Windows](#execução-recorrente-no-windows-com-identidade-gerenciada))
- Credenciais Azure com permissão de leitura nas assinaturas-alvo

## Como iniciar

1. Clone este repositório
2. Crie o ambiente e instale as dependências:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate          # Windows
   # source .venv/bin/activate     # Linux/macOS
   pip install -r requirements.txt
   ```
3. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
4. Execute em ambiente não produtivo:
   ```bash
   python main.py --list                 # lista relatórios disponíveis
   python main.py --report subscriptions # executa um relatório (saída em ./output/)
   python main.py --report all           # executa todos os relatórios de uma vez
   python main.py --report all --output D:\inventario   # outro diretório de saída
   ```
   Por padrão cada relatório é gravado em **`.xlsx` e `.csv`**. Use `--format`
   para escolher apenas um deles (ou defina `AZE_OUTPUT_FORMAT` no `.env`):
   ```bash
   python main.py --report all --format csv    # só CSV
   python main.py --report all --format xlsx   # só Excel (comportamento antigo)
   python main.py --report all --csv-delimiter ";"   # Excel em pt-BR
   ```
   Um CSV guarda uma única tabela: o relatório `resource_details`, que é
   multi-abas, gera um arquivo por aba
   (`resource_details_<aba>_<data-hora>.csv`). O CSV é gravado em `utf-8-sig` —
   sem o BOM, o Excel no Windows lê acentos como Latin-1 e os corrompe.

   Todo arquivo é nomeado `<relatório>_DD_MM_AAAA_HH_MM_SS` — por exemplo
   `resource_groups_21_08_2026_19_45_20.xlsx`. O carimbo é calculado uma única
   vez por execução, então todos os arquivos de uma mesma rodada compartilham o
   mesmo sufixo.

   Como o carimbo tem segundos, **cada execução gera um conjunto novo**: rodar
   duas vezes no mesmo dia não sobrescreve nada, e o diretório de saída acumula
   o histórico. Se isso não for desejado, use `--output` com uma pasta por
   execução (é o que o `Run-AzureEstate.ps1` faz) ou limpe a pasta antes.

   > Arquivos gerados **antes** dessa mudança usavam só a data (`_AAAAMMDD`) e
   > nunca mais serão sobrescritos: eles convivem com os novos, com nomes
   > diferentes e conteúdo equivalente. Para removê-los de uma vez:
   > ```powershell
   > .\scripts\Remove-LegacyOutput.ps1 -WhatIf   # lista o que seria apagado
   > .\scripts\Remove-LegacyOutput.ps1           # apaga, pedindo confirmação
   > ```
   > O script só casa com o padrão antigo; os nomes novos não são tocados. Para
   > os que já foram enviados ao Blob, o `.NOTES` do script traz o comando
   > equivalente com `az storage blob delete-batch`.
5. (Opcional) Envie os relatórios para o Azure Storage. O destino pode ser um
   **container de Blob** ou um **Azure File Share**, por padrão com identidade
   Microsoft Entra (sem chaves de conta):
   ```bash
   # Blob container (recomendado para execução agendada)
   python main.py --report all --upload --upload-target blob \
     --storage-account <conta> --container <container>

   # Azure File Share
   python main.py --report all --upload --upload-target share

   # Apenas envia os .xlsx/.csv já gerados em ./output/
   python main.py --upload
   ```
   O escopo do envio depende de como o comando é invocado: junto com
   `--report`, sobem apenas os arquivos **daquela execução** (identificados
   pelo carimbo), para que um diretório de saída compartilhado não reenvie
   todo o histórico a cada rodada. Sozinho, `--upload` envia tudo que houver
   na pasta — esse é o propósito dele.

   O destino padrão vem de `.env` (`AZE_UPLOAD_TARGET`, `AZE_STORAGE_ACCOUNT` e,
   conforme o caso, `AZE_BLOB_CONTAINER`/`AZE_BLOB_PREFIX` ou `AZE_FILE_SHARE`/
   `AZE_SHARE_PATH`).

   Papéis necessários na storage account — **diferentes para cada destino**:

   | Destino | Papel |
   |---|---|
   | Blob | **Storage Blob Data Contributor** |
   | File Share | **Storage File Data Privileged Contributor** |

   No **Azure Cloud Shell**, o broker de token não consegue emitir tokens de
   data-plane (`storage.azure.com`), então o modo OAuth falha **para File
   Share**. Use o modo de chave (obtida via ARM), que funciona nesse ambiente e
   exige permissão para listar chaves (Contributor / Storage Account
   Contributor):
   ```bash
   python main.py --upload --upload-target share --auth-mode key \
     --subscription <sub-id> --resource-group <rg>
   ```
   O destino **blob** não aceita `--auth-mode key`: ele usa sempre identidade
   Entra.
6. Valide o comportamento antes de qualquer adaptação

## Referência da CLI

Sem `--report` e sem `--upload`, o `main.py` apenas imprime a ajuda.

| Parâmetro | Padrão | Para quê |
|---|---|---|
| `--report NAME` | — | Relatório a executar, ou `all` para todos |
| `--list` | — | Lista os relatórios registrados e sai |
| `--output DIR` | `./output/` | Diretório onde os arquivos são gravados |
| `--format {xlsx,csv,both}` | `AZE_OUTPUT_FORMAT` ou `both` | Formato de saída |
| `--csv-delimiter CHAR` | `AZE_CSV_DELIMITER` ou `,` | Separador de campos do CSV |
| `--upload` | — | Envia os `.xlsx`/`.csv` do diretório de saída ao Storage; com `--report`, só os desta execução |
| `--upload-target {blob,share}` | `AZE_UPLOAD_TARGET` ou `share` | Destino do envio |
| `--storage-account NAME` | `AZE_STORAGE_ACCOUNT` | Conta de armazenamento |
| `--container NAME` | `AZE_BLOB_CONTAINER` | Container (destino `blob`) |
| `--blob-prefix PATH` | `AZE_BLOB_PREFIX` | Pasta virtual no container |
| `--share NAME` | `AZE_FILE_SHARE` | File share (destino `share`) |
| `--share-path PATH` | `AZE_SHARE_PATH` | Diretório dentro do share |
| `--auth-mode {login,key}` | `AZE_UPLOAD_AUTH_MODE` ou `login` | Autenticação do upload; `key` só vale para `share` |
| `--resource-group NAME` | `AZE_RESOURCE_GROUP` | RG da conta, usado por `--auth-mode key` |
| `--subscription ID` | `AZE_SUBSCRIPTION` | Assinatura da conta, usada por `--auth-mode key` |

Todas as variáveis estão documentadas em [`.env.example`](.env.example). Os
nomes antigos com prefixo `ARI_` continuam aceitos por compatibilidade
(`AZE_STORAGE_ACCOUNT` cai para `ARI_STORAGE_ACCOUNT` se a primeira não existir).
A leitura do Azure é configurada por `AZURE_TENANT_ID`, `AZE_AUTH_MODE` e
`AZE_CLIENT_ID`.

## Testes

Não há dependência de Azure: cada script substitui o serviço por um dublê ou
por um servidor local e valida a lógica própria do projeto.

```bash
python testa-csv.py    # nome do arquivo, delimitador, encoding, roteamento de --format
python testa-blob.py   # nome do blob, prefixo, filtro de arquivos, sobrescrita
python testa-auth.py   # cache de token do CachingCredential sob concorrência
python testa-arm.py    # retry do arm_get: 429/503, nextLink, recusa de repetir 403
```

Cada script sai com código diferente de zero se algum caso falhar.

## Execução recorrente no Windows com identidade gerenciada

Para rodar sem usuário logado numa VM do Azure (Tarefa Agendada), a credencial
vem do IMDS da VM — sem `az login`, sem chave, sem segredo em disco.

### 1. Ativar a identidade gerenciada e conceder as permissões

Ative a identidade **atribuída pelo sistema** na VM (é a que o script usa por
padrão) e guarde o principal ID que o comando devolve:

```powershell
# Ativa a identidade do sistema e já retorna o principalId
$principal = az vm identity assign -g <rg-da-vm> -n <vm> `
  --query systemAssignedIdentity -o tsv

# (Se ela já estiver ativa, apenas consulte:)
# $principal = az vm identity show -g <rg-da-vm> -n <vm> --query principalId -o tsv
```

Conceda a ela:

| Escopo | Papel | Para quê |
|---|---|---|
| Management Group / assinaturas-alvo | **Reader** | ler o inventário via Resource Graph |
| Storage Account de destino | **Storage Blob Data Contributor** | gravar os `.xlsx`/`.csv` no container de blob |

```powershell
az role assignment create --assignee $principal --role "Reader" `
  --scope /providers/Microsoft.Management/managementGroups/<mg-id>

az role assignment create --assignee $principal `
  --role "Storage Blob Data Contributor" `
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<conta>
```

As atribuições levam alguns minutos para propagar.

> Se o destino for **File Share** em vez de Blob, o papel é outro:
> **Storage File Data Privileged Contributor**. Não são intercambiáveis.

> Para usar uma identidade **atribuída pelo usuário** em vez da do sistema,
> atribua-a à VM e preencha `AZE_CLIENT_ID` com o *client ID* dela. Se a VM tiver
> mais de uma identidade, `AZE_CLIENT_ID` é obrigatório: o IMDS não adivinha.

### 2. Configurar o `.env` na VM

```ini
AZURE_TENANT_ID=<tenant-id>
AZE_AUTH_MODE=managed-identity
# Identidade do SISTEMA (caso mais comum): deixe AZE_CLIENT_ID vazio.
# Identidade ATRIBUÍDA PELO USUÁRIO: preencha com o client ID dela.
AZE_CLIENT_ID=

AZE_UPLOAD_TARGET=blob
AZE_STORAGE_ACCOUNT=<conta>
AZE_BLOB_CONTAINER=<container>
AZE_BLOB_PREFIX=azure-estate
```

> Para File Share, use `AZE_UPLOAD_TARGET=share` com `AZE_FILE_SHARE` e
> `AZE_SHARE_PATH`. Nesse caso, `AZE_UPLOAD_AUTH_MODE=key` **não** funciona com
> identidade gerenciada: esse modo lista a chave da conta pelo Azure CLI, que
> exige um usuário logado. O destino blob nunca usa chave.

### 3. Testar manualmente antes de agendar

```powershell
.\scripts\Run-AzureEstate.ps1 -Report resource_details -UploadTarget blob
```

O script grava em `output\<data>-<hora>\`, envia os `.xlsx`/`.csv` ao destino
escolhido e registra tudo em `logs\azure-estate_<data>.log`. Ele retorna código
diferente de zero se o Python falhar **ou** se nenhum arquivo for gerado — sem
isso a tarefa apareceria como bem-sucedida para sempre.

| Parâmetro | Padrão | Para quê |
|---|---|---|
| `-Report` | `resource_details` | Relatório a executar (`all` roda todos) |
| `-Format` | `AZE_OUTPUT_FORMAT` | `xlsx`, `csv` ou `both` |
| `-UploadTarget` | `AZE_UPLOAD_TARGET` | `blob` ou `share` |
| `-SkipUpload` | — | Gera os arquivos sem enviar ao Storage |
| `-OutputRoot` | `<repo>\output` | Raiz onde a subpasta datada é criada |
| `-RetentionDays` | `30` | Idade máxima das execuções e logs **locais**; o destino permanente é o Storage |

> A subpasta por execução usa o carimbo `yyyyMMdd-HHmmss` — diferente do nome
> dos arquivos (`DD_MM_AAAA_HH_MM_SS`) porque a limpeza por
> `-RetentionDays` casa esse padrão para decidir o que apagar.

### 4. Registrar a Tarefa Agendada

Em um PowerShell **elevado**:

```powershell
# Diariamente às 03:00, enviando para o container de blob
.\scripts\Install-AzureEstateTask.ps1 -At 03:00 -UploadTarget blob

# Ou toda segunda-feira às 06:30, com todos os relatórios
.\scripts\Install-AzureEstateTask.ps1 -At 06:30 -Weekly Monday -Report all
```

A tarefa roda como **SYSTEM** com "executar mesmo sem usuário logado" (o IMDS é
um endpoint de rede local, acessível ao SYSTEM) e nenhuma senha é armazenada.
Use `-TaskName` para registrar mais de uma tarefa (o padrão é
`AzureEstate-ResourceDetails`, e reexecutar sobrescreve a tarefa de mesmo nome)
e `-User` para trocar a conta de execução.

```powershell
Start-ScheduledTask   -TaskName "AzureEstate-ResourceDetails"   # testar agora
Get-ScheduledTaskInfo -TaskName "AzureEstate-ResourceDetails"   # último resultado
```

## Estrutura

```
azure_estate/
  auth.py              # autenticação Azure (CLI, identidade gerenciada, default)
  config.py            # configuração (tenant, identidade, destino de upload)
  naming.py            # carimbo DD_MM_AAAA_HH_MM_SS dos nomes de arquivo
  enrich.py            # junta SKU/cota, rede e retirements a cada aba
  resource_type_configs.py # tipos de recurso e colunas exportadas
  ari_specs.py         # colunas derivadas do microsoft/ARI (GERADO)
  collectors/          # coleta via Resource Graph, ARM, Advisor
  exporters/           # exportação: Excel/CSV + upload para Azure Storage
    excel.py           #   geração dos .xlsx (com gráficos)
    csv_exporter.py    #   geração dos .csv (um arquivo por tabela)
    blob.py            #   envio para container de Blob (Entra ID)
    file_share.py      #   envio para Azure File Share (OAuth ou chave)
  reports/             # relatórios registrados
scripts/
  Run-AzureEstate.ps1        # execução não assistida (gera, envia, registra log)
  Install-AzureEstateTask.ps1 # registra a Tarefa Agendada do Windows
  Remove-LegacyOutput.ps1    # remove sobras da nomenclatura antiga (_AAAAMMDD)
tools/
  generate_ari_configs.py    # regenera azure_estate/ari_specs.py a partir do ARI
main.py                # CLI
testa-*.py             # testes locais, sem Azure (veja "Testes")
```

## Suporte

Este projeto **não possui SLA nem suporte oficial**.

Veja [SUPPORT.md](./SUPPORT.md) para detalhes.

## Aviso Legal

O uso deste projeto está sujeito aos termos descritos em [DISCLAIMER.md](./DISCLAIMER.md).

## Contribuições

A criação de issues e pull requests é restrita a colaboradores com acesso de
escrita. Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## Licença

Distribuído sob a licença [MIT](LICENSE).

## Marcas Registradas (Trademarks)

Os nomes e serviços da Microsoft são utilizados apenas para fins descritivos.

Este projeto **não é afiliado, endossado ou suportado oficialmente pela Microsoft**.

O uso de marcas da Microsoft não deve sugerir qualquer tipo de parceria ou suporte oficial.
