# Azure Estate

[![ORCID](https://img.shields.io/badge/ORCID-0009--0006--0765--4201-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0006-0765-4201)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4?logo=microsoftazure&logoColor=white)](#)
[![Last commit](https://img.shields.io/github/last-commit/EdneiMonteiro/azure-estate)](https://github.com/EdneiMonteiro/azure-estate/commits)

## Visão Geral

Este repositório contém código de exemplo / prova de conceito (PoC) com o objetivo
de demonstrar como inventariar todo o *estate* de recursos do Azure via **Azure
Resource Graph** e gerar relatórios em **Excel** (assinaturas, grupos de recursos,
tipos de recurso e detalhes de recursos), utilizando Python e Azure Identity.

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

- Coleta de recursos via Azure Resource Graph (`ari/collectors/`)
- Autenticação com `azure-identity` (`DefaultAzureCredential`)
- Exportação para Excel com `openpyxl`/`pandas` (`ari/exporters/`)
- Envio dos relatórios para Azure File Share via Microsoft Entra ID / OAuth (`ari/exporters/file_share.py`)
- Relatórios extensíveis por registro (`ari/reports/`):
  - `subscriptions` — assinaturas
  - `resource_groups` — grupos de recursos
  - `resource_types` — tipos de recurso
  - `resource_details` — detalhes de recursos

## Pré-requisitos

- Python 3.10+
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
   ```
5. (Opcional) Envie os relatórios para um Azure File Share usando a identidade
   Microsoft Entra do usuário logado (OAuth, sem chaves de conta):
   ```bash
   # Gera e envia em seguida
   python main.py --report resource_types --upload

   # Apenas envia os .xlsx já gerados em ./output/
   python main.py --upload
   ```
   O destino padrão vem de `.env` (`ARI_STORAGE_ACCOUNT`, `ARI_FILE_SHARE`,
   `ARI_SHARE_PATH`) e pode ser sobrescrito com `--storage-account`, `--share`
   e `--share-path`. O usuário precisa do papel **Storage File Data Privileged
   Contributor** na storage account, e a conta deve permitir autenticação
   Microsoft Entra (OAuth) para file shares.
6. Valide o comportamento antes de qualquer adaptação

## Estrutura

```
ari/
  auth.py              # autenticação Azure
  config.py            # configuração
  collectors/          # coleta via Resource Graph
  exporters/           # exportação (Excel)
  reports/             # relatórios registrados
main.py                # CLI
```

## Suporte

Este projeto **não possui SLA nem suporte oficial**.

Veja [SUPPORT.md](./SUPPORT.md) para detalhes.

## Aviso Legal

O uso deste projeto está sujeito aos termos descritos em [DISCLAIMER.md](./DISCLAIMER.md).

## Contribuições

Contribuições podem ser aceitas a critério do mantenedor.

## Licença

Distribuído sob a licença [MIT](LICENSE).

## Marcas Registradas (Trademarks)

Os nomes e serviços da Microsoft são utilizados apenas para fins descritivos.

Este projeto **não é afiliado, endossado ou suportado oficialmente pela Microsoft**.

O uso de marcas da Microsoft não deve sugerir qualquer tipo de parceria ou suporte oficial.

## 🤝 Contributing

Issue and pull request creation is restricted to collaborators. See
[CONTRIBUTING.md](CONTRIBUTING.md) for details.
