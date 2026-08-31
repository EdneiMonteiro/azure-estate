"""Verifica o retry do arm_get contra um servidor HTTP local.

Nada de Azure: o que precisa ser provado e a politica de repeticao — 429 com
Retry-After, 503, conexao derrubada, paginacao por nextLink e a recusa de
repetir um erro definitivo (403), que so gastaria tempo.
"""
from __future__ import annotations

import json
import pathlib
import sys
import threading
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import azure_estate.collectors._arm as arm  # noqa: E402

falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    if condicao:
        print(f"  ok   {descricao}")
    else:
        print(f"  FALHA {descricao}")
        falhas.append(descricao)


class _CredencialDuble:
    def get_token(self, *scopes, **kwargs):
        from azure.core.credentials import AccessToken

        return AccessToken("token-de-teste", int(time.time()) + 3600)


# roteiro: lista de respostas a servir, uma por requisicao
ROTEIRO: list[tuple] = []
PEDIDOS: list[str] = []


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        PEDIDOS.append(self.path)
        acao = ROTEIRO.pop(0) if ROTEIRO else ("ok", {"value": []})
        tipo = acao[0]

        if tipo == "drop":
            self.close_connection = True
            self.wfile.close()
            return
        if tipo == "status":
            _, code, retry_after = acao
            corpo = b'{"error":"nope"}'
            self.send_response(code)
            if retry_after is not None:
                self.send_header("Retry-After", str(retry_after))
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)
            return

        corpo = json.dumps(acao[1]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args) -> None:  # silencia o log do servidor
        return

    def handle_one_request(self) -> None:
        # O caso "drop" fecha a conexao no meio da resposta; sem isto o
        # socketserver despeja um traceback que nao e falha de teste.
        try:
            super().handle_one_request()
        except (ValueError, OSError):
            self.close_connection = True


servidor = HTTPServer(("127.0.0.1", 0), _Handler)
BASE = f"http://127.0.0.1:{servidor.server_port}"
threading.Thread(target=servidor.serve_forever, daemon=True).start()
arm.ARM = BASE

CRED = _CredencialDuble()


def roda(roteiro: list[tuple]):
    ROTEIRO.clear()
    ROTEIRO.extend(roteiro)
    PEDIDOS.clear()
    return arm.arm_get(CRED, "/subscriptions/x/usages", "2021-07-01")


print("1. sucesso direto")
linhas = roda([("ok", {"value": [{"a": 1}]})])
checa(linhas == [{"a": 1}], f"valores devolvidos (obtido {linhas})")
checa(len(PEDIDOS) == 1, f"uma unica requisicao (obtido {len(PEDIDOS)})")

print("2. 429 com Retry-After e repetido e respeitado")
t0 = time.time()
linhas = roda([("status", 429, 1), ("ok", {"value": [{"a": 2}]})])
decorrido = time.time() - t0
checa(linhas == [{"a": 2}], "sucesso apos o 429")
checa(len(PEDIDOS) == 2, f"duas requisicoes (obtido {len(PEDIDOS)})")
checa(1.0 <= decorrido < 2.5, f"esperou o Retry-After de 1s (obtido {decorrido:.2f}s)")

print("3. 503 e repetido")
linhas = roda([("status", 503, None), ("ok", {"value": [{"a": 3}]})])
checa(linhas == [{"a": 3}] and len(PEDIDOS) == 2, "sucesso apos 503")

print("4. conexao derrubada e repetida (o erro real do WinError 10054)")
linhas = roda([("drop", ), ("ok", {"value": [{"a": 4}]})])
checa(linhas == [{"a": 4}] and len(PEDIDOS) == 2, "sucesso apos queda de conexao")

print("5. erro definitivo (403) nao e repetido")
try:
    roda([("status", 403, None), ("ok", {"value": [{"a": 5}]})])
    checa(False, "403 propaga excecao")
except urllib.error.HTTPError as exc:
    checa(exc.code == 403, f"HTTPError 403 propagado (obtido {exc.code})")
checa(len(PEDIDOS) == 1, f"nao insistiu (obtido {len(PEDIDOS)} requisicao)")

print("6. falha persistente para em 3 tentativas")
try:
    roda([("status", 503, 0), ("status", 503, 0), ("status", 503, 0), ("ok", {"value": []})])
    checa(False, "excecao propagada")
except urllib.error.HTTPError as exc:
    checa(exc.code == 503, "HTTPError 503 propagado apos as tentativas")
checa(len(PEDIDOS) == 3, f"3 tentativas (obtido {len(PEDIDOS)})")

print("7. paginacao por nextLink continua funcionando, com retry no meio")
linhas = roda(
    [
        ("ok", {"value": [{"a": 1}], "nextLink": f"{BASE}/pagina2?api-version=2021-07-01"}),
        ("status", 429, 0),
        ("ok", {"value": [{"a": 2}]}),
    ]
)
checa(linhas == [{"a": 1}, {"a": 2}], f"duas paginas concatenadas (obtido {linhas})")
checa(PEDIDOS[-1].startswith("/pagina2"), f"segunda pagina buscada (obtido {PEDIDOS[-1]})")

servidor.shutdown()

print()
if falhas:
    print(f"{len(falhas)} FALHA(S):")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)
print("todos os casos passaram")
