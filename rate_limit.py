import time
from collections import defaultdict
from threading import Lock


# ============================================================
# CONFIGURAÇÃO
# ============================================================

LIMITE_POR_HORA = 60       # mensagens por hora por IP
JANELA_SEGUNDOS = 3600


# ============================================================
# ESTADO EM MEMÓRIA
# ============================================================

_lock = Lock()
_historico_ips = defaultdict(list)


def _limpar_antigos(ip: str, agora: float):
    _historico_ips[ip] = [
        t for t in _historico_ips[ip]
        if agora - t < JANELA_SEGUNDOS
    ]


def pode_enviar(ip: str) -> tuple[bool, int]:
    """
    Retorna (permitido, segundos_ate_liberar).
    """
    agora = time.time()

    with _lock:
        _limpar_antigos(ip, agora)

        if len(_historico_ips[ip]) >= LIMITE_POR_HORA:
            mais_antigo = _historico_ips[ip][0]
            tempo_restante = int(
                JANELA_SEGUNDOS - (agora - mais_antigo)
            )
            return False, tempo_restante

        _historico_ips[ip].append(agora)
        return True, 0