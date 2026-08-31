"""Verifica o CsvExporter e o roteamento de formato dos relatorios.

Nada aqui toca no Azure: o que precisa ser provado e a logica local — nome do
arquivo, delimitador, encoding, um CSV por aba e o respeito ao --format.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
from datetime import date

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from azure_estate.exporters.csv_exporter import CsvExporter  # noqa: E402
from azure_estate.reports.base import BaseReport  # noqa: E402

HOJE = date.today().strftime("%Y%m%d")

falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    if condicao:
        print(f"  ok   {descricao}")
    else:
        print(f"  FALHA {descricao}")
        falhas.append(descricao)


def _tmp() -> str:
    return tempfile.mkdtemp()


def _nomes(pasta: str) -> list[str]:
    return sorted(p.name for p in pathlib.Path(pasta).iterdir())


DF = pd.DataFrame(
    [
        {"Nome": "vm-são-paulo", "Qtd. Recursos": 3},
        {"Nome": "vm, com vírgula", "Qtd. Recursos": 1},
    ]
)

print("1. nome padrao e conteudo")
pasta = _tmp()
path = CsvExporter(pasta).save(DF, name="subscriptions")
checa(path.name == f"subscriptions_{HOJE}.csv", f"nome do arquivo (obtido {path.name})")
lido = pd.read_csv(path, encoding="utf-8-sig")
checa(list(lido.columns) == ["Nome", "Qtd. Recursos"], "cabecalho preservado")
checa(lido["Nome"].tolist() == DF["Nome"].tolist(), "acentos e virgulas preservados")
checa(len(lido) == 2, "duas linhas gravadas")

print("2. BOM utf-8 (Excel no Windows le acento sem corromper)")
bruto = path.read_bytes()
checa(bruto.startswith(b"\xef\xbb\xbf"), "arquivo comeca com BOM")

print("3. delimitador configuravel")
pasta = _tmp()
path = CsvExporter(pasta, delimiter=";").save(DF, name="x")
texto = path.read_text(encoding="utf-8-sig")
checa(texto.splitlines()[0] == "Nome;Qtd. Recursos", f"cabecalho com ';' ({texto.splitlines()[0]})")
lido = pd.read_csv(path, sep=";", encoding="utf-8-sig")
checa(lido["Nome"].tolist() == DF["Nome"].tolist(), "campo com virgula continua intacto")

print("4. um CSV por aba, com nome saneado")
pasta = _tmp()
abas = [
    ("Virtual Machines", DF),
    ("Storage/Accounts", DF),
    ("Vazia", pd.DataFrame()),
]
paths = CsvExporter(pasta).save_tables(abas, prefix="resource_details")
checa(len(paths) == 2, f"aba vazia ignorada (obtido {len(paths)})")
checa(
    _nomes(pasta)
    == [
        f"resource_details_Storage_Accounts_{HOJE}.csv",
        f"resource_details_Virtual_Machines_{HOJE}.csv",
    ],
    f"nomes saneados (obtido {_nomes(pasta)})",
)
checa(all("/" not in p.name and "\\" not in p.name for p in paths), "nenhum separador de caminho no nome")

print("5. --format decide o que e gravado")


class _RelatorioFake(BaseReport):
    name = "fake"

    def run(self) -> pd.DataFrame:
        return DF


pasta = _tmp()
_RelatorioFake().export(DF, output_dir=pasta, fmt="csv")
checa(_nomes(pasta) == [f"fake_{HOJE}.csv"], f"fmt=csv gera so CSV (obtido {_nomes(pasta)})")

pasta = _tmp()
_RelatorioFake().export(DF, output_dir=pasta, fmt="xlsx")
checa(_nomes(pasta) == [f"fake_{HOJE}.xlsx"], f"fmt=xlsx gera so XLSX (obtido {_nomes(pasta)})")

pasta = _tmp()
_RelatorioFake().export(DF, output_dir=pasta, fmt="both")
checa(
    _nomes(pasta) == [f"fake_{HOJE}.csv", f"fake_{HOJE}.xlsx"],
    f"fmt=both gera os dois (obtido {_nomes(pasta)})",
)

print("6. diretorio de saida e criado se nao existir")
pasta = str(pathlib.Path(_tmp()) / "novo" / "nivel")
path = CsvExporter(pasta).save(DF, name="y")
checa(path.is_file(), "arquivo gravado em diretorio recem-criado")

print()
if falhas:
    print(f"{len(falhas)} FALHA(S):")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)
print("todos os casos passaram")
