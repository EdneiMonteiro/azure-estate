"""Testa a normalizacao de celulas que o Resource Graph devolve como estrutura.

Roda sem Azure. Uso: python testa-celulas.py
"""

from __future__ import annotations

import sys

from azure_estate.cell_format import flatten_cell
from azure_estate.collectors.resource_details import _rename_row
from azure_estate.resource_type_configs import ResourceTypeConfig

falhas: list[str] = []
total = 0


def checa(rotulo: str, obtido, esperado) -> None:
    global total
    total += 1
    if obtido == esperado:
        print(f"  ok   {rotulo}: {obtido!r}")
    else:
        print(f"  FALHA {rotulo}: obtido {obtido!r}, esperado {esperado!r}")
        falhas.append(rotulo)


print("1. Objetos do tipo SKU viram o nome (a queixa original)")
checa("databricks sku", flatten_cell('{"name":"premium"}'), "premium")
checa(
    "postgres computer size",
    flatten_cell('{"name":"Standard_B2s","tier":"Burstable"}'),
    "Standard_B2s (Burstable)",
)
checa(
    "data explorer",
    flatten_cell('{"name":"Dev(No SLA)_Standard_E2a_v4","tier":"Basic","capacity":1}'),
    "Dev(No SLA)_Standard_E2a_v4 (Basic, 1)",
)
checa(
    "expressroute billing",
    flatten_cell('{"name":"Standard_MeteredData","tier":"Standard","family":"MeteredData"}'),
    "Standard_MeteredData (Standard, MeteredData)",
)
checa("objeto nativo", flatten_cell({"name": "premium"}), "premium")

print("\n2. Listas viram texto legivel")
checa("zona unica", flatten_cell('["2"]'), "2")
checa("varias zonas", flatten_cell('["1","2","3"]'), "1; 2; 3")
checa("lista vazia", flatten_cell("[]"), "")
checa("lista nativa vazia", flatten_cell([]), "")
checa("address space", flatten_cell('["10.139.0.0/16"]'), "10.139.0.0/16")
checa(
    "name servers",
    flatten_cell('["ns1-06.azure-dns.com.","ns2-06.azure-dns.net."]'),
    "ns1-06.azure-dns.com.; ns2-06.azure-dns.net.",
)
checa(
    "lista de objetos",
    flatten_cell('[{"name":"reg-pswd-4bce3dd7-a351"}]'),
    "reg-pswd-4bce3dd7-a351",
)
checa(
    "repr python (aspas simples)",
    flatten_cell("{'dedicated': 'bsa-payments'}"),
    "dedicated=bsa-payments",
)

print("\n3. Escalares atravessam intactos (nao inventar formatacao)")
checa("string comum", flatten_cell("Standard_LRS"), "Standard_LRS")
checa("vazio", flatten_cell(""), "")
checa("nulo", flatten_cell(None), "")
checa("inteiro", flatten_cell(4000), 4000)
checa("booleano", flatten_cell(True), True)
checa("string com chave solta", flatten_cell("{nao e json"), "{nao e json")
checa("cidr sem lista", flatten_cell("10.0.0.0/8"), "10.0.0.0/8")
checa("json invalido preservado", flatten_cell('{"a": '), '{"a": ')

print("\n4. Nenhuma celula sobrevive como JSON serializado")
amostras = [
    '{"name":"premium"}',
    '["2"]',
    "[]",
    '[{"name":"x"}]',
    "{'dedicated': 'bsa-payments'}",
    '{"apiKeyOnly":{}}',
]
sobreviventes = [
    a for a in amostras if str(flatten_cell(a)).strip().startswith(("{", "["))
]
checa("sobreviventes json", sobreviventes, [])

print("\n5. O pipeline aplica a normalizacao (nao so a funcao isolada)")
config = ResourceTypeConfig(
    resource_type="microsoft.databricks/workspaces",
    sheet_name="Databricks",
    columns=[("Pricing Tier", "tostring(sku)"), ("Zonas", "tostring(zones)")],
)
linha = _rename_row(
    {
        "_subName": "sub",
        "resourceGroup": "rg",
        "name": "dbw",
        "location": "brazilsouth",
        "_id": "/x",
        "subscriptionId": "s",
        "_c0": '{"name":"premium"}',
        "_c1": '["1","2"]',
    },
    config,
)[0]
checa("pipeline pricing tier", linha["Pricing Tier"], "premium")
checa("pipeline zonas", linha["Zonas"], "1; 2")
checa("pipeline nao mexe no nome", linha["Nome"], "dbw")

print("\n6. Colunas derivadas tambem passam pela normalizacao")
config_derivado = ResourceTypeConfig(
    resource_type="teste/tipo",
    sheet_name="Teste",
    columns=[],
    raw_columns=[("bruto", "properties")],
    derived=["Pool SKU"],
    derive=lambda raw: [{"Pool SKU": {"name": "Standard_D4s_v3", "tier": "Standard"}}],
)
derivada = _rename_row(
    {"_subName": "s", "resourceGroup": "rg", "name": "n", "location": "l", "_r0": {}},
    config_derivado,
)[0]
checa("derivada normalizada", derivada["Pool SKU"], "Standard_D4s_v3 (Standard)")

print("\n7. Cosmos DB expoe capacidade")
from azure_estate.resource_type_configs import CONFIGS_BY_TYPE  # noqa: E402

cosmos = CONFIGS_BY_TYPE["microsoft.documentdb/databaseaccounts"]
nomes = [n for n, _ in cosmos.columns]
checa("offer type presente", "Offer Type" in nomes, True)
checa("throughput presente", "Limite de Throughput (RU/s)" in nomes, True)
checa("sem coluna duplicada", len(nomes), len(set(nomes)))

print("\n" + "=" * 60)
if falhas:
    print(f"{len(falhas)} de {total} casos falharam: {', '.join(falhas)}")
    sys.exit(1)
print(f"{total}/{total} casos passaram.")
