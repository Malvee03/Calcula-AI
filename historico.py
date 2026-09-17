import json
import uuid
import time
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_RAIZ = Path("historico")
PASTA_RAIZ.mkdir(exist_ok=True)

# Limpa arquivos com mais de 30 dias
DIAS_RETENCAO = 30


# ============================================================
# UTILITÁRIOS DE IP
# ============================================================

def normalizar_ip(ip: str) -> str:
    """
    Converte um IP em nome de pasta seguro.
    Ex.: '192.168.0.10' → 'ip_192_168_0_10'
    """
    if not ip:
        ip = "desconhecido"

    seguro = ip.replace(".", "_").replace(":", "_")
    seguro = "".join(c for c in seguro if c.isalnum() or c == "_")

    return f"ip_{seguro}"


def pasta_do_ip(ip: str) -> Path:
    """Retorna a pasta do IP, criando se não existir."""
    pasta = PASTA_RAIZ / normalizar_ip(ip)
    pasta.mkdir(exist_ok=True)
    return pasta


def obter_ip() -> str:
    """
    Obtém o IP do usuário via headers do Streamlit.
    Funciona local e no Streamlit Cloud.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        from streamlit import runtime

        ctx = get_script_run_ctx()
        if ctx is None:
            return "local"

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return "local"

        # X-Forwarded-For vem do proxy (Streamlit Cloud)
        headers = session_info.request.headers
        forwarded = headers.get("X-Forwarded-For")

        if forwarded:
            return forwarded.split(",")[0].strip()

        return session_info.request.client.host

    except Exception:
        return "local"


# ============================================================
# ID DE CONVERSA
# ============================================================

def gerar_id_conversa() -> str:
    return uuid.uuid4().hex[:12]


def caminho_conversa(ip: str, conversa_id: str) -> Path:
    return pasta_do_ip(ip) / f"conversa_{conversa_id}.json"


# ============================================================
# SALVAR
# ============================================================

def salvar_conversa(
    ip: str,
    conversa_id: str,
    mensagens: list,
    titulo: str = "Nova conversa"
):
    """Salva uma conversa no disco, dentro da pasta do IP."""
    caminho = caminho_conversa(ip, conversa_id)

    dados = {
        "id": conversa_id,
        "titulo": titulo,
        "criada_em": datetime.now().isoformat(),
        "atualizada_em": datetime.now().isoformat(),
        "mensagens": mensagens
    }

    # Preserva data de criação se já existir
    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                antigo = json.load(f)
                dados["criada_em"] = antigo.get(
                    "criada_em",
                    dados["criada_em"]
                )
        except Exception:
            pass

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    return conversa_id


# ============================================================
# CARREGAR
# ============================================================

def carregar_conversa(ip: str, conversa_id: str) -> dict | None:
    """Carrega uma conversa específica do IP."""
    caminho = caminho_conversa(ip, conversa_id)

    if not caminho.exists():
        return None

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def listar_conversas(ip: str) -> list:
    """
    Lista as conversas do IP, mais recentes primeiro.
    """
    pasta = pasta_do_ip(ip)
    conversas = []

    for arquivo in pasta.glob("conversa_*.json"):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            conversas.append({
                "id": dados.get("id"),
                "titulo": dados.get("titulo", "Sem título"),
                "atualizada_em": dados.get("atualizada_em", ""),
                "num_mensagens": len(dados.get("mensagens", []))
            })
        except Exception:
            continue

    conversas.sort(
        key=lambda c: c["atualizada_em"],
        reverse=True
    )

    return conversas


# ============================================================
# DELETAR
# ============================================================

def deletar_conversa(ip: str, conversa_id: str) -> bool:
    caminho = caminho_conversa(ip, conversa_id)

    if caminho.exists():
        caminho.unlink()
        return True

    return False


# ============================================================
# LIMPEZA AUTOMÁTICA
# ============================================================

def limpar_conversas_antigas():
    """
    Remove arquivos com mais de DIAS_RETENCAO dias.
    Chamado uma vez por sessão.
    """
    agora = time.time()
    limite = agora - (DIAS_RETENCAO * 86400)

    for arquivo in PASTA_RAIZ.rglob("conversa_*.json"):
        try:
            if arquivo.stat().st_mtime < limite:
                arquivo.unlink()
        except Exception:
            continue


# ============================================================
# TÍTULO
# ============================================================

def gerar_titulo_a_partir_mensagem(mensagem: str) -> str:
    if not mensagem:
        return "Nova conversa"

    titulo = mensagem.strip().split("\n")[0]

    if len(titulo) > 50:
        titulo = titulo[:47] + "..."

    return titulo