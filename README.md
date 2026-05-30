# ARI — Azure Resource Inventory

Ferramenta de linha de comando em Python que inventaria recursos do Azure via
**Azure Resource Graph** e gera relatórios em **Excel** (assinaturas, grupos de
recursos, tipos de recurso e detalhes de recursos).

## Funcionalidades

- Coleta via Azure Resource Graph (`ari/collectors/`)
- Autenticação com `azure-identity` (`DefaultAzureCredential`)
- Exportação para Excel com `openpyxl`/`pandas` (`ari/exporters/`)
- Relatórios extensíveis por registro (`ari/reports/`):
  - `subscriptions` — assinaturas
  - `resource_groups` — grupos de recursos
  - `resource_types` — tipos de recurso
  - `resource_details` — detalhes de recursos

## Requisitos

- Python 3.10+
- Credenciais Azure com permissão de leitura nas assinaturas-alvo

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
cp .env.example .env            # ajuste as variáveis
```

## Uso

```bash
# Listar relatórios disponíveis
python main.py --list

# Executar um relatório (saída em ./output/ por padrão)
python main.py --report subscriptions

# Diretório de saída customizado
python main.py --report subscriptions --output /tmp/ari
```

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

## Licença

Distribuído sob a licença [MIT](LICENSE).
