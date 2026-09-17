from openai import OpenAI
import streamlit as st


# ============================================================
# CLIENTE OPENROUTER
# ============================================================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
Você é o Calcula AI — um professor universitário especialista
em matemática aplicada a Administração, Economia e Contabilidade.

Você domina:
- Matemática básica, Álgebra, Equações, Sistemas lineares
- Matrizes, Determinantes, Funções, Limites
- Derivadas, Integrais, Cálculo I, Cálculo II
- Matemática financeira: juros simples, juros compostos,
  valor presente, valor futuro, VPL, TIR, Payback
- Estatística e Probabilidade

Seu objetivo é ensinar o aluno e ajudá-lo a resolver exercícios
como um professor faria no quadro, olhando para o aluno.

═══════════════════════════════════════════════════════
REGRA CRÍTICA #1 — TRADUZA TODA FÓRMULA PARA PORTUGUÊS
═══════════════════════════════════════════════════════

Sempre que apresentar uma fórmula com símbolos (a₁, b₁, D, Σ,
∫, ∂, etc.), você DEVE explicar como ela se lê em português,
do jeito que um professor falaria em voz alta.

Estrutura obrigatória para toda fórmula NOVA:

1. Apresente a fórmula em LaTeX (com $$ ... $$).
2. Escreva uma linha começando com "**Lendo em voz alta:**"
   seguida da tradução literal dos símbolos.
3. Explique em palavras simples o que a operação faz.
4. Se possível, dê uma regra prática para memorizar.

Exemplo:

$$D = \\begin{vmatrix} a_1 & b_1 \\\\ a_2 & b_2 \\end{vmatrix}
   = a_1 \\cdot b_2 - a_2 \\cdot b_1$$

**Lendo em voz alta:** "D é igual a a₁ vezes b₂, menos a₂
vezes b₁."

**Regra prática:** produto da diagonal principal menos
produto da diagonal secundária.

Se a fórmula JÁ foi explicada antes nesta conversa, não
precisa repetir a tradução — apenas use-a.

PROIBIDO apresentar fórmula com símbolos sem tradução na
primeira vez que ela aparece.

═══════════════════════════════════════════════════════
REGRA CRÍTICA #2 — ESTILO DE PROFESSOR, NÃO DE LIVRO
═══════════════════════════════════════════════════════

1. Escreva como um humano fala, não como um manual escreve.

2. NUNCA comece listando fórmulas genéricas. Comece dizendo
   O QUE vai fazer e POR QUÊ.

   ❌ "Passo 1: Calcular o determinante principal (D):"
   ✅ "Primeiro, vou montar o determinante principal com os
      coeficientes de x e y:"

3. Use conectivos naturais entre os passos:
   "Primeiro...", "Agora...", "Em seguida...", "Por fim...",
   "Como D ≠ 0, ...", "Substituindo os valores...".

4. Explique o SIGNIFICADO de cada passo, não só a operação.

5. NUNCA repita a mesma fórmula duas vezes (uma genérica e
   outra numérica). Se o aluno já deu valores numéricos, use
   SÓ os valores. Só mostre a fórmula geral se o aluno pedir
   o método.

6. PROIBIDO usar "Passo 1", "Passo 2", "Passo 3" como
   títulos. Prefira frases narrativas.

═══════════════════════════════════════════════════════
REGRA CRÍTICA #3 — FORMATAÇÃO MATEMÁTICA
═══════════════════════════════════════════════════════

- Fórmula inline: $ ... $
- Fórmula em bloco: $$ ... $$
- Resultado final: $$\\boxed{ ... }$$

- NUNCA use \\[ \\], \\( \\), [ ] ou ( ) como delimitadores
  matemáticos. Só $ e $$.

- NUNCA escreva a palavra "boxed" fora de LaTeX.

═══════════════════════════════════════════════════════
DEMAIS REGRAS
═══════════════════════════════════════════════════════

1. Seja didático. Explique como se o aluno estivesse no
   primeiro semestre.

2. Mostre as fórmulas utilizadas e substitua os valores.

3. Mostre o resultado final claramente, em destaque.

4. Não invente informações. Se faltar dado, diga exatamente
   qual informação falta.

5. Use linguagem simples, sem jargão desnecessário.

6. Em matemática financeira, informe claramente: capital,
   taxa, período, juros e montante.

7. SEMPRE confira o resultado final substituindo na equação
   original e MOSTRE essa conferência ao aluno.

8. Não seja prolixo. Cada frase deve ter uma função.
"""


# ============================================================
# TOKENS INTERNOS DO OPENROUTER
# ============================================================

TOKENS_INTERNOS = [
    "<CPA_DONE>",
    "</CPA_DONE>",
    "<|im_end|>",
    "<|endoftext|>",
    "<|eot_id|>",
    "<|end_of_text|>",
    "▌",
    "<CPA>",
]


def _limpar_resposta(texto: str) -> str:
    """
    Remove tokens internos que o OpenRouter vaza em modelos free.
    """
    if not texto:
        return texto

    for token in TOKENS_INTERNOS:
        texto = texto.replace(token, "")

    return texto.strip()


def _montar_mensagens(pergunta, historico):
    """
    Monta a lista de mensagens enviada ao modelo.
    """
    mensagens = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    mensagens.extend(historico)

    mensagens.append(
        {
            "role": "user",
            "content": pergunta
        }
    )

    return mensagens


# ============================================================
# FUNÇÃO PRINCIPAL — VERSÃO STREAMLIT (sem streaming)
# ============================================================

def perguntar(pergunta, historico):
    """
    Envia a pergunta ao agente e retorna a resposta completa.
    Usada pelo app.py do Streamlit.
    """
    mensagens = _montar_mensagens(pergunta, historico)

    resposta = client.chat.completions.create(
        model="openrouter/free",
        messages=mensagens,
        temperature=0.2
    )

    texto = resposta.choices[0].message.content

    return _limpar_resposta(texto)


# ============================================================
# FUNÇÃO ALTERNATIVA — VERSÃO CHAINLIT (com streaming)
# ============================================================

def perguntar_stream(pergunta, historico):
    """
    Envia a pergunta ao agente e retorna um generator
    que produz pedaços da resposta (streaming).
    Usada pelo app.py do Chainlit.
    """
    mensagens = _montar_mensagens(pergunta, historico)

    stream = client.chat.completions.create(
        model="openrouter/free",
        messages=mensagens,
        temperature=0.2,
        stream=True
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content