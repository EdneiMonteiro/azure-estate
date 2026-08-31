"""Verifica o cache de token do CachingCredential sem tocar no Azure.

O que precisa ser provado: uma unica aquisicao serve muitas threads, o token
expirado e renovado, a falha transitoria e repetida e o azure-core aceita o
wrapper como credencial (senao o cache existiria e nunca seria usado).
"""
from __future__ import annotations

import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from azure.core.credentials import AccessToken, AccessTokenInfo  # noqa: E402

from azure_estate.auth import CachingCredential  # noqa: E402

falhas: list[str] = []


def checa(condicao: bool, descricao: str) -> None:
    if condicao:
        print(f"  ok   {descricao}")
    else:
        print(f"  FALHA {descricao}")
        falhas.append(descricao)


class _CredencialDuble:
    """Imita o AzureCliCredential: lento, sem cache e as vezes falha."""

    def __init__(self, ttl: int = 3600, falhas_iniciais: int = 0, atraso: float = 0.05) -> None:
        self.chamadas = 0
        self._ttl = ttl
        self._falhas = falhas_iniciais
        self._atraso = atraso
        self._lock = threading.Lock()

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        with self._lock:
            self.chamadas += 1
            restam = self._falhas
            self._falhas = max(0, self._falhas - 1)
        time.sleep(self._atraso)
        if restam > 0:
            raise RuntimeError("Failed to invoke the Azure CLI")
        return AccessToken("t%d" % self.chamadas, int(time.time()) + self._ttl)

    def get_token_info(self, *scopes, options=None) -> AccessTokenInfo:
        token = self.get_token(*scopes, **(options or {}))
        return AccessTokenInfo(token.token, token.expires_on)


ESCOPO = "https://management.azure.com/.default"

print("1. 64 threads compartilham uma unica aquisicao")
duble = _CredencialDuble()
cred = CachingCredential(duble)
with ThreadPoolExecutor(max_workers=16) as pool:
    tokens = list(pool.map(lambda _: cred.get_token(ESCOPO).token, range(64)))
checa(duble.chamadas == 1, f"credencial interna chamada 1x (obtido {duble.chamadas})")
checa(len(set(tokens)) == 1, "todas as threads receberam o mesmo token")

print("2. escopos diferentes nao se misturam")
duble = _CredencialDuble()
cred = CachingCredential(duble)
a = cred.get_token(ESCOPO).token
b = cred.get_token("https://storage.azure.com/.default").token
checa(duble.chamadas == 2, f"uma aquisicao por escopo (obtido {duble.chamadas})")
checa(a != b, "tokens distintos por escopo")

print("3. token proximo do vencimento e renovado")
# TTL menor que a margem de renovacao (300 s): o cache nunca deve servi-lo.
duble = _CredencialDuble(ttl=60)
cred = CachingCredential(duble)
cred.get_token(ESCOPO)
cred.get_token(ESCOPO)
checa(duble.chamadas == 2, f"renovou dentro da margem (obtido {duble.chamadas})")

duble = _CredencialDuble(ttl=3600)
cred = CachingCredential(duble)
cred.get_token(ESCOPO)
cred.get_token(ESCOPO)
checa(duble.chamadas == 1, f"token valido nao e renovado (obtido {duble.chamadas})")

print("4. falha transitoria do CLI e repetida")
duble = _CredencialDuble(falhas_iniciais=2)
cred = CachingCredential(duble)
checa(cred.get_token(ESCOPO).token != "", "token obtido apos 2 falhas")
checa(duble.chamadas == 3, f"3 tentativas (obtido {duble.chamadas})")

print("5. falha persistente propaga o erro original")
duble = _CredencialDuble(falhas_iniciais=99)
cred = CachingCredential(duble)
try:
    cred.get_token(ESCOPO)
    checa(False, "excecao propagada")
except RuntimeError as exc:
    checa("Azure CLI" in str(exc), f"mensagem original preservada ({exc})")
checa(duble.chamadas == 3, f"parou em 3 tentativas (obtido {duble.chamadas})")

print("6. azure-core aceita o wrapper (senao o cache seria ignorado)")
from azure.core.pipeline import PipelineRequest, PipelineContext  # noqa: E402
from azure.core.pipeline.policies import BearerTokenCredentialPolicy  # noqa: E402
from azure.core.rest import HttpRequest  # noqa: E402

duble = _CredencialDuble()
cred = CachingCredential(duble)
policy = BearerTokenCredentialPolicy(cred, ESCOPO)
for _ in range(3):
    pedido = PipelineRequest(
        HttpRequest("GET", "https://management.azure.com/subscriptions"),
        PipelineContext(None),
    )
    policy.on_request(pedido)
    cabecalho = pedido.http_request.headers.get("Authorization", "")
checa(cabecalho.startswith("Bearer t"), f"header Authorization preenchido ({cabecalho})")
checa(duble.chamadas == 1, f"policy reaproveitou o cache (obtido {duble.chamadas})")

print("7. get_credential devolve o wrapper")
from azure_estate.auth import get_credential  # noqa: E402

checa(isinstance(get_credential(), CachingCredential), "get_credential embrulha a credencial")

print()
if falhas:
    print(f"{len(falhas)} FALHA(S):")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)
print("todos os casos passaram")
