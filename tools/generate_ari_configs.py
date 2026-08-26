"""Generate azure_estate/ari_specs.py from the microsoft/ARI PowerShell modules.

microsoft/ARI (MIT, https://github.com/microsoft/ARI) curates, per resource type,
which Azure properties are worth reporting.  This tool parses those modules and
re-expresses the same field selection as Resource Graph column specs.

Two things make a naive port fail, and both are handled here:

1. PowerShell property access is case-insensitive, so ARI writes
   ``$data.networkprofile.networkplugin``.  KQL is case-SENSITIVE and returns an
   empty string for the wrong casing.  Every path is therefore corrected against
   the real JSON returned by the tenant.
2. ARI emits one row per nested item (node pool, security rule, …).  Those
   columns are collected into an ``explode`` spec instead of scalar columns.

Usage:  python tools/generate_ari_configs.py [--ari-path DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure.mgmt.resourcegraph import ResourceGraphClient  # noqa: E402

from azure_estate.auth import get_credential  # noqa: E402
from azure_estate.collectors._graph import run_graph_query  # noqa: E402
from azure_estate.collectors.subscriptions import list_active_subscriptions  # noqa: E402
from azure_estate.config import TENANT_ID  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(REPO, "azure_estate", "ari_specs.py")

TYPE_RE = re.compile(r"TYPE\s*-(?:eq|in)\s*\(?((?:\s*'[^']+'\s*,?)+)\)?", re.I)
LIT_RE = re.compile(r"'([^']+)'")
ASSIGN_RE = re.compile(r"^\s*\$(\w+)\s*=\s*(.+)$", re.M)
FOREACH_RE = re.compile(r"foreach\s*\(\s*\$(\w+)\s+in\s+(\$[\w.]+)", re.I)
KEY_RE = re.compile(r"^\s*'([^']+)'\s*=\s*(.+?);?\s*$", re.M)
SHEET_RE = re.compile(r"Excel Sheet Name:\s*(.+)", re.I)
SPLIT_RE = re.compile(r"\.split\(\s*'/'\s*\)\s*\[\s*(\d+)\s*\]", re.I)

# Columns that are structural, come from another API, or are produced by joins
# across resources.  They are reported but not generated.
IGNORAR_COLUNAS = {
    "ID", "Subscription", "Resource Group", "Name", "Location", "Resource U",
    "Tag Name", "Tag Value", "Retiring Feature", "Retiring Date",
    "RetiredFeature", "RetiredDate", "Retirement Date", "Retiring Reason",
}
RAIZES = ("properties", "sku", "identity", "plan", "kind", "zones", "managedby")


# ---------------------------------------------------------------------------
# 1. Parse the ARI modules
# ---------------------------------------------------------------------------
def _bloco_hash(txt: str, inicio: int) -> str:
    i = txt.index("@{", inicio) + 2
    nivel, ini = 1, i
    while i < len(txt) and nivel:
        if txt[i] == "{":
            nivel += 1
        elif txt[i] == "}":
            nivel -= 1
        i += 1
    return txt[ini:i - 1]


def _resolver(expr: str, txt: str, aliases: dict[str, str], visto: set[str] | None = None) -> set[str]:
    """Resolve a PowerShell expression into the property paths it reads."""
    visto = visto or set()
    out: set[str] = set()
    for var, sufixo in re.findall(r"\$(\w+)((?:\.\w+)*)", expr):
        v = var.lower()
        if v == "data":
            if sufixo:
                out.add("properties" + sufixo.lower())
        elif v in aliases:
            out.add(aliases[v] + sufixo.lower() if sufixo else aliases[v])
        elif v == "1":
            # $1 is the whole resource: $1.zones, $1.kind, $1.sku, ...
            if sufixo:
                out.add(sufixo.lstrip(".").lower())
        elif v in ("sub1", "tag", "tags", "obj", "tmp", "resucount") or v.startswith("_"):
            continue
        elif var not in visto:
            for nome, rhs in ASSIGN_RE.findall(txt):
                if nome.lower() == v:
                    out |= _resolver(rhs, txt, aliases, visto | {nome, var})
                    break
    return out


def _aliases_foreach(txt: str) -> dict[str, str]:
    """Map each `foreach ($x in ...)` alias to the property path it iterates.

    ARI often assigns the array to a variable first, so the right-hand side is
    resolved through the surrounding assignments.
    """
    aliases: dict[str, str] = {}
    for _ in range(4):  # a few passes let aliases defined via other aliases settle
        mudou = False
        for var, origem in FOREACH_RE.findall(txt):
            if var.lower() in aliases:
                continue
            caminhos = {
                p for p in _resolver(origem, txt, aliases)
                if p.split(".")[0] in RAIZES
            }
            if caminhos:
                aliases[var.lower()] = sorted(caminhos, key=len)[0]
                mudou = True
        if not mudou:
            break
    return aliases


def parse_ari(raiz_ari: str) -> list[dict[str, Any]]:
    """Return one record per ARI module (a module is one Excel sheet)."""
    modulos: list[dict[str, Any]] = []
    for raiz, _, arquivos in os.walk(raiz_ari):
        for arq in sorted(arquivos):
            if not arq.endswith(".ps1"):
                continue
            txt = open(os.path.join(raiz, arq), encoding="utf-8-sig", errors="replace").read()
            tipos: set[str] = set()
            for grupo in TYPE_RE.findall(txt):
                tipos |= {t.lower() for t in LIT_RE.findall(grupo) if t.lower().startswith("microsoft.")}
            if not tipos:
                continue
            sheet = SHEET_RE.search(txt)
            sheet = sheet.group(1).strip() if sheet else os.path.splitext(arq)[0]
            aliases = _aliases_foreach(txt)
            colunas: dict[str, set[str]] = {}
            splits: dict[str, int] = {}
            for m in re.finditer(r"\$(?:obj|tmp\d*)\s*=\s*(?:\[pscustomobject\])?\s*@\{", txt, re.I):
                for nome, rhs in KEY_RE.findall(_bloco_hash(txt, m.start())):
                    if nome in IGNORAR_COLUNAS:
                        continue
                    colunas.setdefault(nome, set())
                    colunas[nome] |= _resolver(rhs, txt, aliases)
                    # `.Split('/')[N]` pulls one segment out of a resource id;
                    # the segment index is part of the column's meaning.
                    indice = _indice_split(rhs, txt)
                    if indice is not None:
                        splits.setdefault(nome, indice)
            modulos.append(
                {
                    "module": f"{os.path.basename(raiz)}/{arq}",
                    "sheet": sheet,
                    "types": sorted(tipos),
                    "colunas": colunas,
                    "splits": splits,
                    "arrays": set(aliases.values()),
                }
            )
    return modulos


def _indice_split(expr: str, txt: str, visto: set[str] | None = None) -> int | None:
    """Segment index of a `.Split('/')[N]` in *expr*, following assignments."""
    visto = visto or set()
    m = SPLIT_RE.search(expr)
    if m:
        return int(m.group(1))
    for var, _sufixo in re.findall(r"\$(\w+)((?:\.\w+)*)", expr):
        if var in visto:
            continue
        for nome, rhs in ASSIGN_RE.findall(txt):
            if nome.lower() == var.lower():
                achado = _indice_split(rhs, txt, visto | {var, nome})
                if achado is not None:
                    return achado
                break
    return None


# ---------------------------------------------------------------------------
# 2. Learn the real casing (and existence) of every path from the tenant
# ---------------------------------------------------------------------------
def _caminhar(valor: Any, prefixo: str, mapa: dict[str, str], arrays: set[str]) -> None:
    if isinstance(valor, dict):
        for k, v in valor.items():
            caminho = f"{prefixo}.{k}" if prefixo else k
            mapa.setdefault(caminho.lower(), caminho)
            _caminhar(v, caminho, mapa, arrays)
    elif isinstance(valor, list):
        # Arrays are traversed transparently, matching how PowerShell (and thus
        # ARI's property paths) reach into every item at once.  The path is
        # recorded so the collector knows it cannot be a plain KQL projection.
        arrays.add(prefixo.lower())
        for item in valor[:20]:
            _caminhar(item, prefixo, mapa, arrays)


def mapa_de_caixa(tipos: list[str], amostras: int) -> dict[str, dict[str, Any]]:
    cred = get_credential()
    subs = [s["subscription_id"] for s in list_active_subscriptions(cred, TENANT_ID)]
    cl = ResourceGraphClient(cred)
    mapas: dict[str, dict[str, Any]] = {}
    for i, t in enumerate(tipos, 1):
        kql = (
            f"Resources | where type == '{t}' "
            f"| project properties, sku, identity, plan, kind, zones, managedBy | take {amostras}"
        )
        try:
            linhas = run_graph_query(cl, subs, kql)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{i}/{len(tipos)}] {t}: ERRO {exc}".encode("ascii", "replace").decode())
            mapas[t] = {"paths": {}, "arrays": []}
            continue
        mapa: dict[str, str] = {}
        arrays: set[str] = set()
        for linha in linhas:
            for raiz in ("properties", "sku", "identity", "plan"):
                valor = linha.get(raiz)
                if valor:
                    mapa.setdefault(raiz, raiz)
                    _caminhar(valor, raiz, mapa, arrays)
            # scalar/array columns that live at the resource root
            for raiz, real in (("kind", "kind"), ("zones", "zones"), ("managedby", "managedBy")):
                if linha.get(real):
                    mapa.setdefault(raiz, real)
        mapas[t] = {"paths": mapa, "arrays": sorted(arrays)}
        print(f"  [{i}/{len(tipos)}] {t}: {len(linhas)} amostra(s), {len(mapa)} caminho(s)")
    return mapas


# ---------------------------------------------------------------------------
# 3. Turn resolved paths into column specs
# ---------------------------------------------------------------------------
def corrigir(path: str, mapa: dict[str, str]) -> tuple[str | None, str]:
    """Return (corrected_path, status)."""
    p = path.lower()
    if p in mapa:
        return mapa[p], "ok"
    # ARI's `.count` on an array -> array_length of the parent
    if p.endswith(".count") and p[: -len(".count")] in mapa:
        return mapa[p[: -len(".count")]], "contagem"
    # ARI's `.split('/')[8]` -> one segment out of a resource id
    if p.endswith(".split") and p[: -len(".split")] in mapa:
        return mapa[p[: -len(".split")]], "split"
    if not mapa:
        return path[: -len(".split")] if p.endswith(".split") else path, "sem_amostra"
    return None, "inexistente"


def _bracket(path: str) -> str:
    """Render a property path as string indexing: properties['a']['b'].

    Dotted access collides with KQL keywords — `properties.title`,
    `properties.ipFilterRules.count` and `properties.x.split` are all rejected
    as invalid queries.  String indexing is immune to the whole class.
    """
    partes = path.split(".")
    return partes[0] + "".join(f"['{p}']" for p in partes[1:])


def kql_de(path: str, status: str) -> str:
    if status == "contagem":
        return f"tostring(array_length({_bracket(path)}))"
    if status.startswith("split"):
        indice = status.split(":")[1]
        return f"tostring(split(tostring({_bracket(path)}), '/')[{indice}])"
    return f"tostring({_bracket(path)})"


def _colunas_do_par(reg: dict[str, Any], info: dict[str, Any]) -> tuple[dict, dict]:
    """Build the column specs a module would yield for one candidate type.

    Columns fall into three shapes:
      * ``columns`` — a plain, case-correct KQL projection;
      * ``multi``   — the path crosses an array, so KQL cannot project it; the
                      array is fetched raw and the values joined in Python;
      * ``explode`` — the path lives under the module's iterated array, which
                      ARI renders as one row per item.
    """
    mapa: dict[str, str] = info.get("paths", {})
    arrays_reais: set[str] = set(info.get("arrays", []))

    arrays = {a for a in reg["arrays"] if corrigir(a, mapa)[1] in ("ok", "sem_amostra")}
    pontos = {a: 0 for a in arrays}
    for paths in reg["colunas"].values():
        for p in paths:
            for a in arrays:
                if p.startswith(a + "."):
                    pontos[a] += 1
    eixo = max(pontos, key=pontos.get) if pontos and max(pontos.values()) else None
    eixo_real = corrigir(eixo, mapa)[0] if eixo else None

    colunas, multi, explode_cols, vistos = [], [], [], set()
    perdidas: dict[str, list[str]] = {"externas": [], "inexistentes": []}
    for nome, paths in sorted(reg["colunas"].items()):
        uteis = sorted(p for p in paths if p.split(".")[0] in RAIZES)
        if not uteis:
            perdidas["externas"].append(nome)
            continue
        escolhido = None
        for p in uteis:
            real, status = corrigir(p, mapa)
            if real and status != "inexistente":
                escolhido = (p, real, status)
                break
        if not escolhido:
            perdidas["inexistentes"].append(f"{nome} <- {uteis[0]}")
            continue
        p, real, status = escolhido
        if real in vistos:
            continue
        vistos.add(real)
        # A column built with `.Split('/')[N]` reports one id segment, whatever
        # the property path itself resolved to.
        if nome in reg["splits"] and status != "contagem":
            status = f"split:{reg['splits'][nome]}"
        elif status == "split":
            status = "split:8"
        if eixo and p.startswith(eixo + "."):
            sufixo = real[len(eixo_real) + 1:] if eixo_real and real.startswith(eixo_real) else real
            explode_cols.append([nome, sufixo, status])
            continue
        raiz_array = _array_atravessado(p, arrays_reais)
        if raiz_array:
            raiz_real = mapa.get(raiz_array, raiz_array)
            sufixo = real[len(raiz_real) + 1:] if real.startswith(raiz_real + ".") else ""
            multi.append([nome, raiz_real, sufixo, status])
        else:
            colunas.append([nome, kql_de(real, status)])

    spec = {"columns": colunas, "multi": multi, "explode": explode_cols, "eixo": eixo_real}
    return spec, perdidas


def _array_atravessado(path: str, arrays_reais: set[str]) -> str | None:
    """Return the outermost ancestor of *path* that is a JSON array, if any."""
    partes = path.lower().split(".")
    for i in range(1, len(partes)):
        prefixo = ".".join(partes[:i])
        if prefixo in arrays_reais:
            return prefixo
    return None


def gerar(modulos: list[dict[str, Any]], mapas: dict[str, dict[str, Any]]) -> tuple[list[dict], dict]:
    """Pick, for every resource type, the ARI module that truly describes it.

    A module also references auxiliary types (it joins NICs, flow logs, …) and a
    type may be referenced by several modules.  The owning module is the one
    whose columns resolve against the type's real properties, which is decided
    per type rather than by module, so no type is dropped.
    """
    melhor: dict[str, tuple] = {}
    for reg in modulos:
        for tipo in reg["types"]:
            spec, perdidas = _colunas_do_par(reg, mapas.get(tipo, {}))
            n = len(spec["columns"]) + len(spec["multi"]) + len(spec["explode"])
            if not n:
                continue
            atual = melhor.get(tipo)
            if atual is None or n > atual[0]:
                melhor[tipo] = (n, reg, spec, perdidas)

    specs, relatorio = [], {"externas": {}, "inexistentes": {}, "sem_colunas": []}
    for tipo, (_n, reg, s, perdidas) in sorted(melhor.items()):
        spec = {
            "type": tipo,
            "sheet": reg["sheet"][:31],
            "module": reg["module"],
            "columns": s["columns"],
        }
        if s["multi"]:
            spec["multi"] = s["multi"]
        if s["explode"] and s["eixo"]:
            spec["explode"] = [s["eixo"], s["explode"]]
        specs.append(spec)
        for chave, itens in perdidas.items():
            if itens:
                relatorio[chave][tipo] = itens
    relatorio["sem_colunas"] = sorted(
        {t for m in modulos for t in m["types"]} - set(melhor)
    )
    return specs, relatorio


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ari-path", help="Local clone of microsoft/ARI (cloned on demand otherwise).")
    ap.add_argument("--samples", type=int, default=30, help="Resources sampled per type to learn casing.")
    ap.add_argument("--cache", help="JSON file caching the learned casing map between runs.")
    args = ap.parse_args()

    raiz = args.ari_path
    tmp = None
    if not raiz:
        tmp = tempfile.mkdtemp(prefix="ari-")
        print(f"Clonando microsoft/ARI em {tmp} ...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "-q", "https://github.com/microsoft/ARI.git", tmp],
            check=True,
        )
        raiz = tmp
    raiz = os.path.join(raiz, "Modules", "Public", "InventoryModules")

    print("Lendo modulos do ARI ...")
    modulos = parse_ari(raiz)
    tipos = sorted({t for m in modulos for t in m["types"]})
    print(f"  {len(modulos)} modulo(s), {len(tipos)} tipo(s) de recurso referenciados")

    cache = {}
    if args.cache and os.path.exists(args.cache):
        cache = json.load(open(args.cache, encoding="utf-8"))
    faltando = [t for t in tipos if t not in cache]
    if faltando:
        print("Aprendendo a caixa real das propriedades no tenant ...")
        cache.update(mapa_de_caixa(faltando, args.samples))
        if args.cache:
            json.dump(cache, open(args.cache, "w", encoding="utf-8"), ensure_ascii=False)
    else:
        print(f"Caixa reaproveitada de {args.cache}")
    mapas = cache

    specs, relatorio = gerar(modulos, mapas)
    total = sum(
        len(s["columns"]) + len(s.get("multi", [])) + len(s.get("explode", ["", []])[1])
        for s in specs
    )
    print(f"Gerado: {len(specs)} tipo(s), {total} coluna(s)")

    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write('"""Column specs derived from the microsoft/ARI inventory modules.\n\n')
        f.write("GENERATED FILE - do not edit by hand.\n")
        f.write("Regenerate with:  python tools/generate_ari_configs.py\n\n")
        f.write("Source: https://github.com/microsoft/ARI (MIT License, Copyright (c) 2020 RenatoGregio).\n")
        f.write("Property paths are case-corrected against live Azure Resource Graph data,\n")
        f.write("because KQL - unlike PowerShell - is case-sensitive on dynamic fields.\n")
        f.write('"""\n\nfrom __future__ import annotations\n\n')
        f.write("ARI_SPECS: list[dict] = ")
        json.dump(specs, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"Escrito: {SAIDA}")

    rel = os.path.join(REPO, "ari_relatorio.json")
    json.dump(relatorio, open(rel, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Relatorio de colunas nao geradas: {rel}")
    if tmp:
        print(f"(clone temporario em {tmp})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
