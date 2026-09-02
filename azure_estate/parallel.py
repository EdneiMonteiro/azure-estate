"""Mapeamento paralelo que sobrevive à falta de threads no sistema operacional.

Em máquinas com pouca memória livre, ``ThreadPoolExecutor`` levanta
``RuntimeError: can't start new thread`` ao tentar reservar a pilha de cada
thread.  Isso derrubava a execução inteira no meio do enriquecimento.  Aqui a
falha vira degradação: menos threads, e no limite execução serial — mais lenta,
porém completa.  O aviso é sempre visível; um fallback silencioso esconderia
uma máquina no fim dos recursos.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def _e_falta_de_thread(exc: RuntimeError) -> bool:
    """Só a exaustão de threads do interpretador, não qualquer erro que cite threads.

    O CPython usa "can't start new thread"; outras runtimes usam "create".
    Casar apenas por "thread" faria um erro de negócio ser retentado três vezes.
    """
    msg = str(exc).lower()
    return "start new thread" in msg or "create new thread" in msg


def _degraus(workers: int) -> list[int]:
    """Sequência de tentativas, da mais paralela até a serial."""
    passos: list[int] = []
    atual = max(int(workers), 1)
    while atual > 1:
        passos.append(atual)
        atual //= 4
    passos.append(1)
    return passos


def map_resiliente(
    fn: Callable[[T], R],
    itens: Iterable[T],
    workers: int,
    rotulo: str,
) -> list[R]:
    """Aplica *fn* a *itens* em paralelo, caindo para serial se faltar thread.

    *fn* precisa ser idempotente: numa degradação a lista é reprocessada do
    início.  Nos dois usos atuais são requisições GET, então é seguro.
    """
    lista = list(itens)
    if not lista:
        return []

    for tentativa, atual in enumerate(_degraus(workers)):
        try:
            if atual <= 1:
                return [fn(item) for item in lista]
            with ThreadPoolExecutor(max_workers=atual) as pool:
                return list(pool.map(fn, lista))
        except RuntimeError as exc:
            if not _e_falta_de_thread(exc):
                raise
            print(
                f"\n  [AVISO] o sistema recusou novas threads em {rotulo} "
                f"({atual} worker(s)). Reduzindo o paralelismo e refazendo.",
                end="",
                flush=True,
            )
            if tentativa == 0:
                continue

    # Inalcançável: o último degrau é serial e não cria thread alguma.
    return [fn(item) for item in lista]
