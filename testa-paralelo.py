"""Testa a degradacao para execucao serial quando o SO recusa threads.

Simula o RuntimeError observado na VM ("can't start new thread") sem depender
do Azure nem de esgotar memoria de verdade.

Uso: python testa-paralelo.py
"""

from __future__ import annotations

import concurrent.futures
import io
import sys
from contextlib import redirect_stdout

import azure_estate.parallel as paralelo
from azure_estate.parallel import _degraus, map_resiliente

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


class PoolQueRecusa:
    """Duble de ThreadPoolExecutor que recusa acima de *limite* workers."""

    def __init__(self, limite: int, contador: list[int]):
        self.limite = limite
        self.contador = contador

    def __call__(self, max_workers: int):
        self.contador.append(max_workers)
        if max_workers > self.limite:
            raise RuntimeError("can't start new thread")
        return concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)


def com_pool(limite: int, itens, workers=16):
    """Roda map_resiliente com o duble; devolve (resultado, tentativas, saida)."""
    contador: list[int] = []
    original = paralelo.ThreadPoolExecutor
    paralelo.ThreadPoolExecutor = PoolQueRecusa(limite, contador)  # type: ignore[assignment]
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            resultado = map_resiliente(lambda x: x * 2, itens, workers, "teste")
    finally:
        paralelo.ThreadPoolExecutor = original  # type: ignore[assignment]
    return resultado, contador, buffer.getvalue()


entrada = list(range(20))
esperado = [x * 2 for x in entrada]

print("1. Caminho feliz: paralelismo total, sem aviso")
res, tentativas, saida = com_pool(limite=64, itens=entrada)
checa("resultado", res, esperado)
checa("uma unica tentativa", tentativas, [16])
checa("sem aviso", saida, "")

print("\n2. SO recusa 16 threads: cai um degrau e ENTREGA o mesmo resultado")
res, tentativas, saida = com_pool(limite=8, itens=entrada)
checa("resultado completo", res, esperado)
checa("tentou 16 depois 4", tentativas, [16, 4])
checa("avisou", "[AVISO]" in saida, True)

print("\n3. SO recusa qualquer thread: cai para serial e ainda entrega")
res, tentativas, saida = com_pool(limite=0, itens=entrada)
checa("resultado completo", res, esperado)
checa("todos os degraus tentados", tentativas, [16, 4])
checa("avisou duas vezes", saida.count("[AVISO]"), 2)
checa("serial nao criou pool", len(tentativas), 2)

print("\n4. RuntimeError de outra causa NAO e mascarado (mesmo citando 'thread')")


def explode(_):
    raise RuntimeError("falha ao gravar no banco, e nao de thread")


chamadas: list[int] = []


def conta_e_explode(x):
    chamadas.append(x)
    return explode(x)


try:
    with redirect_stdout(io.StringIO()):
        map_resiliente(conta_e_explode, [1], 1, "teste")
    checa("propagou", "nao levantou", "RuntimeError")
except RuntimeError as exc:
    checa("propagou a mensagem original", str(exc), "falha ao gravar no banco, e nao de thread")
    checa("nao retentou", len(chamadas), 1)

print("\n5. Degraus vao do paralelo ate o serial, sem repetir")
checa("degraus de 16", _degraus(16), [16, 4, 1])
checa("degraus de 8", _degraus(8), [8, 2, 1])
checa("degraus de 1", _degraus(1), [1])
checa("degraus de 0", _degraus(0), [1])

print("\n6. Lista vazia nao cria thread alguma")
res, tentativas, saida = com_pool(limite=0, itens=[])
checa("resultado vazio", res, [])
checa("nenhuma tentativa", tentativas, [])

print("\n7. Os dois call sites reais usam o helper")
import inspect  # noqa: E402

import azure_estate.collectors.compute_skus as skus  # noqa: E402

fonte = inspect.getsource(skus)
checa("map_resiliente nos dois call sites", fonte.count("map_resiliente("), 2)
checa("nenhum ThreadPoolExecutor solto", "ThreadPoolExecutor" in fonte, False)

print("\n" + "=" * 60)
if falhas:
    print(f"{len(falhas)} de {total} casos falharam: {', '.join(falhas)}")
    sys.exit(1)
print(f"{total}/{total} casos passaram.")
