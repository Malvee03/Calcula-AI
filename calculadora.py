import sympy as sp
import numpy as np


# ============================================================
# EQUAÇÕES
# ============================================================

def resolver_equacao(equacao):

    equacao = equacao.replace("^", "**")

    esquerda, direita = equacao.split("=")

    x = sp.symbols("x")

    expressao = (
        sp.sympify(esquerda)
        - sp.sympify(direita)
    )

    return sp.solve(expressao, x)


# ============================================================
# DERIVADA
# ============================================================

def derivada(expressao):

    x = sp.symbols("x")

    expressao = expressao.replace("^", "**")

    expr = sp.sympify(expressao)

    return sp.diff(expr, x)


# ============================================================
# INTEGRAL
# ============================================================

def integral(expressao):

    x = sp.symbols("x")

    expressao = expressao.replace("^", "**")

    expr = sp.sympify(expressao)

    return sp.integrate(expr, x)


# ============================================================
# LIMITE
# ============================================================

def limite(expressao, ponto):

    x = sp.symbols("x")

    expressao = expressao.replace("^", "**")

    expr = sp.sympify(expressao)

    return sp.limit(
        expr,
        x,
        ponto
    )


# ============================================================
# SIMPLIFICAÇÃO
# ============================================================

def simplificar(expressao):

    x = sp.symbols("x")

    expressao = expressao.replace("^", "**")

    expr = sp.sympify(expressao)

    return sp.simplify(expr)


# ============================================================
# JUROS SIMPLES
# ============================================================

def juros_simples(
    capital,
    taxa,
    tempo
):

    montante = (
        capital *
        (1 + taxa * tempo)
    )

    juros = montante - capital

    return {
        "capital": capital,
        "juros": juros,
        "montante": montante
    }


# ============================================================
# JUROS COMPOSTOS
# ============================================================

def juros_compostos(
    capital,
    taxa,
    tempo
):

    montante = (
        capital *
        ((1 + taxa) ** tempo)
    )

    juros = montante - capital

    return {
        "capital": capital,
        "juros": juros,
        "montante": montante
    }


# ============================================================
# VALOR PRESENTE
# ============================================================

def valor_presente(
    valor_futuro,
    taxa,
    tempo
):

    return (
        valor_futuro /
        ((1 + taxa) ** tempo)
    )


# ============================================================
# VALOR FUTURO
# ============================================================

def valor_futuro(
    valor_presente,
    taxa,
    tempo
):

    return (
        valor_presente *
        ((1 + taxa) ** tempo)
    )


# ============================================================
# VPL
# ============================================================

def vpl(
    taxa,
    fluxos
):

    resultado = 0

    for periodo, fluxo in enumerate(fluxos):

        resultado += (
            fluxo /
            ((1 + taxa) ** periodo)
        )

    return resultado


# ============================================================
# PAYBACK
# ============================================================

def payback(fluxos):

    acumulado = 0

    for periodo, fluxo in enumerate(fluxos):

        acumulado += fluxo

        if acumulado >= 0:

            saldo_anterior = (
                acumulado - fluxo
            )

            if fluxo == 0:
                return periodo

            fracao = (
                abs(saldo_anterior)
                / fluxo
            )

            return periodo - 1 + fracao

    return None


# ============================================================
# ESTATÍSTICA
# ============================================================

def estatistica(valores):

    valores = np.array(valores)

    return {

        "quantidade": len(valores),

        "media": float(
            np.mean(valores)
        ),

        "mediana": float(
            np.median(valores)
        ),

        "variancia": float(
            np.var(valores)
        ),

        "desvio_padrao": float(
            np.std(valores)
        )
    }