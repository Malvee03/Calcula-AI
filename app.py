import streamlit as st
from agente import perguntar, perguntar_stream
from historico import (
    gerar_id_conversa,
    salvar_conversa,
    carregar_conversa,
    listar_conversas,
    deletar_conversa,
    gerar_titulo_a_partir_mensagem,
    obter_ip,
    limpar_conversas_antigas
)
from rate_limit import pode_enviar


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Calcula AI",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# LIMPEZA AUTOMÁTICA
# ============================================================

if "limpeza_feita" not in st.session_state:
    limpar_conversas_antigas()
    st.session_state.limpeza_feita = True


# ============================================================
# IDENTIFICAÇÃO DO USUÁRIO
# ============================================================

if "ip_usuario" not in st.session_state:
    st.session_state.ip_usuario = obter_ip()

ip_usuario = st.session_state.ip_usuario


# ============================================================
# ESTADO INICIAL
# ============================================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "conversa_id" not in st.session_state:
    st.session_state.conversa_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processando" not in st.session_state:
    st.session_state.processando = False

# Processa delete via URL (?apagar=ID)
params = st.query_params
if "apagar" in params:
    id_apagar = params["apagar"]
    deletar_conversa(ip_usuario, id_apagar)
    if id_apagar == st.session_state.conversa_id:
        st.session_state.conversa_id = gerar_id_conversa()
        st.session_state.messages = []
    st.query_params.clear()
    st.rerun()

if st.session_state.conversa_id is None:
    conversas = listar_conversas(ip_usuario)
    if conversas:
        ultima = conversas[0]
        dados = carregar_conversa(ip_usuario, ultima["id"])
        if dados:
            st.session_state.conversa_id = ultima["id"]
            st.session_state.messages = dados["mensagens"]
    if st.session_state.conversa_id is None:
        st.session_state.conversa_id = gerar_id_conversa()


# ============================================================
# VARIÁVEIS DE TEMA
# ============================================================

if st.session_state.dark_mode:
    bg           = "#0f0f10"
    bg_sidebar   = "#18181b"
    border       = "#2d2d30"
    text         = "#e4e4e7"
    text_strong  = "#ffffff"
    text_muted   = "#a1a1aa"
    text_faint   = "#71717a"
    input_bg     = "#18181b"
    scheme       = "dark"
else:
    bg           = "#ffffff"
    bg_sidebar   = "#f9f9f8"
    border       = "#e4e4e7"
    text         = "#1f2937"
    text_strong  = "#111827"
    text_muted   = "#6b7280"
    text_faint   = "#9ca3af"
    input_bg     = "#ffffff"
    scheme       = "light"


# ============================================================
# CSS
# ============================================================

st.markdown(
    f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"], button, input, textarea, select {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }}

    /* FUNDO */
    html, body {{
        background: {bg} !important;
        color: {text} !important;
        color-scheme: {scheme} only !important;
    }}

    .stApp {{ background: {bg} !important; }}

    /* HEADER */
    header[data-testid="stHeader"],
    header[data-testid="stHeader"] *,
    [data-testid="stHeader"] {{
        background: {bg} !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stToolbar"],
    [data-testid="stToolbar"] *,
    [data-testid="stToolbarActions"],
    [data-testid="stToolbarActions"] *,
    [data-testid="stDecoration"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stMainMenu"],
    [data-testid="stMainMenu"] * {{
        background: transparent !important;
        color: {text_strong} !important;
        fill: {text_strong} !important;
    }}

    /* ============================================================
       SETA DE EXPANDIR/RECOLHER SIDEBAR
       ============================================================ */

    /* Botão de expandir (sidebar recolhida) */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] *,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] * {{
        color: {text_strong} !important;
        fill: {text_strong} !important;
    }}

    /* SVG da seta */
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="stSidebarCollapsedControl"] svg *,
    [data-testid="collapsedControl"] svg *,
    [data-testid="stSidebarCollapseButton"] svg * {{
        fill: {text_strong} !important;
        color: {text_strong} !important;
        stroke: {text_strong} !important;
    }}

    /* Botão clicável em si */
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="collapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button {{
        color: {text_strong} !important;
        background: transparent !important;
        border: none !important;
        opacity: 1 !important;
    }}

    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="collapsedControl"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover {{
        color: {text_strong} !important;
        background: {bg_sidebar} !important;
    }}

    /* SIDEBAR */
    [data-testid="stSidebar"] {{
        background: {bg_sidebar} !important;
        border-right: 1px solid {border} !important;
    }}

    [data-testid="stSidebar"] * {{ color: {text} !important; }}

    .sidebar-brand {{
        font-size: 16px;
        font-weight: 700;
        color: {text_strong} !important;
        margin: 0 0 2px 4px;
        line-height: 1.2;
    }}

    .sidebar-brand-sub {{
        font-size: 12px;
        color: {text_faint} !important;
        margin: 0 0 24px 4px;
    }}

    .sidebar-label {{
        font-size: 11px;
        font-weight: 600;
        color: {text_faint} !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 20px 0 8px 4px;
    }}

    .sidebar-item {{
        font-size: 13px;
        color: {text_muted} !important;
        padding: 6px 8px;
        line-height: 1.5;
    }}

    /* ============================================================
       BOTÕES DA SIDEBAR
       ============================================================ */

    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        text-align: left;
        background: {bg} !important;
        background-color: {bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        color: {text} !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 0.5rem 0.75rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 1.4 !important;
        min-height: 40px !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        border-color: {text_faint} !important;
        color: {text_strong} !important;
    }}

    [data-testid="stSidebar"] .stButton > button * {{
        background: transparent !important;
        color: inherit !important;
    }}

    /* ============================================================
       BOTÃO × EM HTML PURO
       ============================================================ */

    .btn-del-conversa {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        height: 40px !important;
        background: {bg_sidebar} !important;
        background-color: {bg_sidebar} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        color: {text_strong} !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        text-align: center !important;
        line-height: 1 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
        box-sizing: border-box !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    .btn-del-conversa:hover {{
        background: {bg} !important;
        background-color: {bg} !important;
        border-color: {text_faint} !important;
        color: {text_strong} !important;
        text-decoration: none !important;
    }}

    .btn-del-conversa:visited,
    .btn-del-conversa:active {{
        color: {text_strong} !important;
        text-decoration: none !important;
    }}

    /* ============================================================
       ESCONDE BOTÕES DE AÇÃO DO CHAT
       ============================================================ */

    [data-testid="stChatMessageActions"],
    [data-testid="stChatMessageActions"] *,
    [data-testid="stElementToolbar"],
    [data-testid="stElementToolbar"] * {{
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }}

    /* TEXTO GERAL */
    .main, .main * {{ color: {text}; }}

    .main h1, .main h2, .main h3,
    .main h4, .main h5, .main h6,
    .main strong {{ color: {text_strong} !important; }}

    /* CHAT */
    [data-testid="stChatMessage"] .stMarkdown,
    [data-testid="stChatMessage"] .stMarkdown *,
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] em {{ color: {text} !important; }}

    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] h1,
    [data-testid="stChatMessage"] h2,
    [data-testid="stChatMessage"] h3,
    [data-testid="stChatMessage"] a {{ color: {text_strong} !important; }}

    /* KATEX */
    .katex, .katex * {{ color: {text_strong} !important; }}

    .katex-display {{
        background: {bg_sidebar};
        padding: 14px 18px;
        border-radius: 10px;
        border-left: 3px solid {border};
        margin: 12px 0;
        overflow-x: auto !important;
        max-width: 100% !important;
    }}

    /* TYPING */
    .typing-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 6px 0;
    }}

    .typing-indicator span {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: {text_faint};
        display: inline-block;
        animation: typing-bounce 1.4s infinite ease-in-out both;
    }}

    .typing-indicator span:nth-child(1) {{ animation-delay: -0.32s; }}
    .typing-indicator span:nth-child(2) {{ animation-delay: -0.16s; }}
    .typing-indicator span:nth-child(3) {{ animation-delay: 0s; }}

    @keyframes typing-bounce {{
        0%, 80%, 100% {{ transform: scale(0.7); opacity: 0.4; }}
        40% {{ transform: scale(1); opacity: 1; }}
    }}

    /* INPUT */
    [data-testid="stChatInput"] {{
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        background: {input_bg} !important;
        box-shadow: none !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {text_strong} !important;
        -webkit-text-fill-color: {text_strong} !important;
        background: transparent !important;
        caret-color: {text_strong} !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {text_faint} !important;
        -webkit-text-fill-color: {text_faint} !important;
    }}

    /* BARRA DE INPUT */
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottomBlockContainer"] > div {{
        background: {bg} !important;
        border: none !important;
        box-shadow: none !important;
    }}

    /* ESTADO VAZIO */
    .empty-state {{
        text-align: center;
        padding: 12vh 20px 0 20px;
    }}

    .empty-title {{
        font-size: 28px;
        font-weight: 600;
        color: {text_strong} !important;
        letter-spacing: -0.02em;
        margin: 0 0 12px 0;
    }}

    .empty-sub {{
        font-size: 15px;
        color: {text_muted} !important;
        line-height: 1.7;
        max-width: 440px;
        margin: 0 auto;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-brand">Calcula AI</div>'
        '<div class="sidebar-brand-sub">Assistente de matemática</div>',
        unsafe_allow_html=True
    )

    if st.button("+  Nova conversa", use_container_width=True, key="nova"):
        if st.session_state.messages:
            salvar_conversa(
                ip_usuario,
                st.session_state.conversa_id,
                st.session_state.messages,
                titulo=gerar_titulo_a_partir_mensagem(
                    st.session_state.messages[0]["content"]
                )
            )
        st.session_state.conversa_id = gerar_id_conversa()
        st.session_state.messages = []
        st.rerun()

    icone_tema = "🌙  Modo escuro" if not st.session_state.dark_mode else "☀️  Modo claro"
    if st.button(icone_tema, use_container_width=True, key="toggle_tema"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.divider()

    st.markdown(
        '<div class="sidebar-label">Suas conversas</div>',
        unsafe_allow_html=True
    )

    conversas = listar_conversas(ip_usuario)

    if not conversas:
        st.markdown(
            '<div class="sidebar-item" style="opacity:0.5;">'
            'Nenhuma conversa ainda'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for conversa in conversas:
            id_conv = conversa["id"]
            titulo = conversa["titulo"]
            ativa = id_conv == st.session_state.conversa_id

            titulo_curto = titulo if len(titulo) <= 22 else titulo[:19] + "..."
            marcador = "● " if ativa else ""
            label = f"{marcador}{titulo_curto}"

            col_nome, col_del = st.columns([6, 1])

            with col_nome:
                if st.button(
                    label,
                    key=f"conv_{id_conv}",
                    use_container_width=True
                ):
                    if st.session_state.messages and st.session_state.conversa_id != id_conv:
                        salvar_conversa(
                            ip_usuario,
                            st.session_state.conversa_id,
                            st.session_state.messages,
                            titulo=gerar_titulo_a_partir_mensagem(
                                st.session_state.messages[0]["content"]
                            )
                        )
                    dados = carregar_conversa(ip_usuario, id_conv)
                    if dados:
                        st.session_state.conversa_id = id_conv
                        st.session_state.messages = dados["mensagens"]
                        st.rerun()

            with col_del:
                st.markdown(
                    f'<a class="btn-del-conversa" '
                    f'href="?apagar={id_conv}" '
                    f'title="Apagar conversa">×</a>',
                    unsafe_allow_html=True
                )

    st.divider()

    st.markdown(
        '<div class="sidebar-label">Tópicos</div>'
        '<div class="sidebar-item">Cálculo I e II</div>'
        '<div class="sidebar-item">Álgebra linear</div>'
        '<div class="sidebar-item">Matemática financeira</div>'
        '<div class="sidebar-item">Estatística</div>'
        '<div class="sidebar-item">Análise de investimentos</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ÁREA PRINCIPAL
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-title">Como posso ajudar?</div>
            <div class="empty-sub">
                Digite um exercício de cálculo, álgebra, matemática
                financeira ou estatística. Vou resolver passo a passo,
                explicando cada etapa.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    for mensagem in st.session_state.messages:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])


# ============================================================
# INPUT + RESPOSTA
# ============================================================

pergunta = st.chat_input(
    "Digite seu exercício...",
    disabled=st.session_state.processando
)


if pergunta and not st.session_state.processando:

    st.session_state.processando = True

    permitido, tempo_restante = pode_enviar(ip_usuario)

    if not permitido:
        minutos = max(1, tempo_restante // 60)
        st.warning(
            f"⏱️ Você atingiu o limite de 60 mensagens por hora. "
            f"Tente novamente em {minutos} minutos."
        )
        st.session_state.processando = False
        st.stop()

    st.session_state.messages.append(
        {"role": "user", "content": pergunta}
    )

    with st.chat_message("user"):
        st.markdown(pergunta)

    titulo = gerar_titulo_a_partir_mensagem(
        st.session_state.messages[0]["content"]
    )
    salvar_conversa(
        ip_usuario,
        st.session_state.conversa_id,
        st.session_state.messages,
        titulo=titulo
    )

    with st.chat_message("assistant"):

        placeholder = st.empty()

        placeholder.markdown(
            '<div class="typing-indicator">'
            '<span></span><span></span><span></span>'
            '</div>',
            unsafe_allow_html=True
        )

        resposta_completa = ""

        try:
            for pedaco in perguntar_stream(
                pergunta,
                st.session_state.messages[:-1]
            ):
                resposta_completa += pedaco
                placeholder.markdown(resposta_completa)

        except Exception as erro:
            import traceback
            traceback.print_exc()
            resposta_completa = (
                "❌ Ocorreu um erro ao processar seu exercício.\n\n"
                f"**Detalhes:** `{str(erro)}`"
            )
            placeholder.markdown(resposta_completa)

    st.session_state.messages.append(
        {"role": "assistant", "content": resposta_completa}
    )

    salvar_conversa(
        ip_usuario,
        st.session_state.conversa_id,
        st.session_state.messages,
        titulo=titulo
    )

    st.session_state.processando = False

    st.rerun()