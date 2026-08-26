"""Verifica o BlobUploader sem tocar no Azure.

O cliente de blob e substituido por um duble que apenas registra as chamadas.
O que precisa ser provado aqui e a logica local: nome do blob, prefixo,
normalizacao de separadores, filtro de arquivos e sobrescrita — o transporte em
si e responsabilidade do SDK.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from azure_estate.exporters.blob import BlobUploader  # noqa: E402


class _ContainerDuble:
    def __init__(self) -> None:
        self.chamadas: list[tuple[str, bool, bytes]] = []
        self.criado = False

    def create_container(self) -> None:
        self.criado = True

    def upload_blob(self, name, data, overwrite):  # noqa: ANN001
        self.chamadas.append((name, overwrite, data.read()))


def _uploader(prefix: str = "", **kw) -> tuple[BlobUploader, _ContainerDuble]:
    up = BlobUploader("conta", "container", prefix, credential=object(), **kw)
    duble = _ContainerDuble()
    up._container_client = lambda: duble  # type: ignore[method-assign]
    return up, duble


def _pasta(nomes: list[str]) -> pathlib.Path:
    tmp = pathlib.Path(tempfile.mkdtemp())
    for n in nomes:
        (tmp / n).write_bytes(n.encode())
    return tmp


falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    if condicao:
        print(f"  ok   {descricao}")
    else:
        print(f"  FALHA {descricao}")
        falhas.append(descricao)


print("1. nome do blob sem prefixo")
up, duble = _uploader()
pasta = _pasta(["a.xlsx"])
enviados = up.upload_directory(pasta)
checa(enviados == ["a.xlsx"], f"retorno == ['a.xlsx'] (obtido {enviados})")
checa(duble.chamadas[0][0] == "a.xlsx", "blob nomeado 'a.xlsx'")
checa(duble.chamadas[0][1] is True, "overwrite=True")
checa(duble.chamadas[0][2] == b"a.xlsx", "conteudo do arquivo enviado")

print("2. prefixo simples")
up, duble = _uploader("relatorios")
enviados = up.upload_directory(_pasta(["a.xlsx"]))
checa(enviados == ["relatorios/a.xlsx"], f"prefixo aplicado (obtido {enviados})")

print("3. prefixo com barras invertidas e sobrando")
up, duble = _uploader("\\\\azure\\estate\\\\")
enviados = up.upload_directory(_pasta(["a.xlsx"]))
checa(
    enviados == ["azure/estate/a.xlsx"],
    f"separadores normalizados e bordas removidas (obtido {enviados})",
)
checa("\\" not in enviados[0], "nenhuma barra invertida no nome do blob")

print("4. so .xlsx e enviado")
up, duble = _uploader()
enviados = up.upload_directory(_pasta(["a.xlsx", "b.txt", "c.log", "d.xlsx"]))
checa(sorted(enviados) == ["a.xlsx", "d.xlsx"], f"filtro *.xlsx (obtido {enviados})")

print("5. pasta vazia e pasta inexistente")
up, duble = _uploader()
checa(up.upload_directory(_pasta([])) == [], "pasta vazia devolve []")
checa(up.upload_directory("C:/nao/existe/mesmo") == [], "pasta inexistente devolve []")
checa(duble.chamadas == [], "nenhuma chamada de upload disparada")

print("6. target_uri")
up, _ = _uploader()
checa(
    up.target_uri == "https://conta.blob.core.windows.net/container",
    f"sem prefixo (obtido {up.target_uri})",
)
up, _ = _uploader("x/y")
checa(
    up.target_uri == "https://conta.blob.core.windows.net/container/x/y",
    f"com prefixo (obtido {up.target_uri})",
)

print("7. container nao e criado por padrao")
up, duble = _uploader()
up.upload_directory(_pasta(["a.xlsx"]))
checa(duble.criado is False, "create_container nao chamado sem create_container=True")

print()
if falhas:
    print(f"{len(falhas)} FALHA(S):")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)
print("todos os casos passaram")
