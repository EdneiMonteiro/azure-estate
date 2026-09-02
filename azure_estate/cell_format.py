"""Normalização de células que o Resource Graph devolve como objeto ou lista.

O ARM devolve muitos campos como estrutura (``sku`` é ``{"name": "premium"}``,
``zones`` é ``["2"]``).  Quando essas estruturas chegam à planilha sem
tratamento, a célula vira JSON cru — tecnicamente presente, praticamente
inútil.  Este módulo converte a estrutura no valor que a pessoa esperava ler.
"""

from __future__ import annotations

import ast
import json
from typing import Any

# Chaves que identificam o "valor principal" de um objeto do tipo SKU.
_NAME_KEYS = ("name", "value", "id", "displayName")

# Chaves acessórias que valem como qualificador entre parênteses.
_QUALIFIER_KEYS = ("tier", "family", "size", "capacity")

_JOIN = "; "
_MAX_DEPTH = 3


def _parse_maybe(value: str) -> Any:
    """Devolve a estrutura embutida em *value*, ou o próprio *value*."""
    texto = value.strip()
    if not texto or texto[0] not in "{[":
        return value
    try:
        return json.loads(texto)
    except (ValueError, TypeError):
        pass
    try:
        # O Graph às vezes chega como objeto Python já convertido em repr.
        return ast.literal_eval(texto)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return value


def _scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _flatten_dict(value: dict[str, Any], depth: int) -> str:
    if not value:
        return ""

    principal = next(
        (k for k in _NAME_KEYS if isinstance(value.get(k), (str, int, float))),
        None,
    )
    if principal is not None:
        texto = _scalar(value[principal])
        qualificadores = [
            _scalar(value[k])
            for k in _QUALIFIER_KEYS
            if isinstance(value.get(k), (str, int, float, bool))
            and _scalar(value[k]).lower() not in ("", texto.lower())
        ]
        if qualificadores:
            texto = f"{texto} ({', '.join(qualificadores)})"
        return texto

    if depth >= _MAX_DEPTH:
        return json.dumps(value, ensure_ascii=False)

    partes = []
    for chave, item in value.items():
        rendido = _flatten(item, depth + 1)
        if rendido != "":
            partes.append(f"{chave}={rendido}")
    return _JOIN.join(partes)


def _flatten(value: Any, depth: int = 0) -> Any:
    if value is None:
        return ""
    if isinstance(value, str):
        estrutura = _parse_maybe(value)
        if isinstance(estrutura, str):
            return estrutura
        return _flatten(estrutura, depth)
    if isinstance(value, dict):
        return _flatten_dict(value, depth)
    if isinstance(value, (list, tuple)):
        if not value:
            return ""
        if depth >= _MAX_DEPTH:
            return json.dumps(list(value), ensure_ascii=False)
        partes = [str(_flatten(item, depth + 1)) for item in value]
        return _JOIN.join(p for p in partes if p != "")
    return value


def flatten_cell(value: Any) -> Any:
    """Devolve *value* legível: objetos viram o nome, listas viram texto unido.

    Escalares (str, int, bool) atravessam sem alteração — só estruturas, e
    strings que contêm estruturas serializadas, são reescritas.
    """
    return _flatten(value, 0)
