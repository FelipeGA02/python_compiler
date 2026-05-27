"""
tests/test_completo.py — Suíte de testes BRL.

Cobre, de acordo com a especificação da linguagem:
  • Programa válido completo (exemplo.LC)
  • Erros léxicos   — 5 casos
  • Erros sintáticos — 7 casos
  • Erros semânticos — 15 casos
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lexer.lexer import tokenize_string
from src.parser.parser import parse_tokens
from src.semantic.semantic_analyzer import analyze
from src.utils.error import LexicalError
from src.utils.error import SyntaxError as BRLSyntaxError
from src.utils.error import SemanticError

# ── Infraestrutura ───────────────────────────────────────────────────────────

_pass = 0
_fail = 0


def _pipeline(source: str) -> None:
    tokens, _ = tokenize_string(source)
    ast       = parse_tokens(tokens)
    analyze(ast)


def _ok(label: str) -> None:
    global _pass
    _pass += 1
    print(f"  PASS  {label}")


def _fail_test(label: str, reason: str) -> None:
    global _fail
    _fail += 1
    print(f"  FAIL  {label}")
    print(f"        {reason}")


def test_ok(label: str, source: str) -> None:
    try:
        _pipeline(source)
        _ok(label)
    except Exception as e:
        _fail_test(label, f"erro inesperado: {e}")


def test_lex(label: str, source: str) -> None:
    try:
        _pipeline(source)
        _fail_test(label, "nenhum erro foi lançado")
    except LexicalError:
        _ok(label)
    except Exception as e:
        _fail_test(label, f"esperado LexicalError, obtido {type(e).__name__}: {e}")


def test_syn(label: str, source: str) -> None:
    try:
        _pipeline(source)
        _fail_test(label, "nenhum erro foi lançado")
    except BRLSyntaxError:
        _ok(label)
    except Exception as e:
        _fail_test(label, f"esperado SyntaxError, obtido {type(e).__name__}: {e}")


def test_sem(label: str, source: str) -> None:
    try:
        _pipeline(source)
        _fail_test(label, "nenhum erro foi lançado")
    except SemanticError:
        _ok(label)
    except Exception as e:
        _fail_test(label, f"esperado SemanticError, obtido {type(e).__name__}: {e}")


# Wrapper mínimo: envolve o corpo dentro de um programa BRL válido
_BASE = "inicio prog ;\n{body}\nfim\n"


def _prog(body: str) -> str:
    return _BASE.format(body=body)


# =============================================================================
# VÁLIDO — exemplo.LC completo (deve passar as 3 fases)
# =============================================================================

def suite_valido() -> None:
    print("\n=== VÁLIDO ===")
    path = os.path.join(os.path.dirname(__file__), "exemplo.LC")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    test_ok("VAL-01  exemplo.LC — programa completo da especificação", source)


# =============================================================================
# ERROS LÉXICOS
# =============================================================================

def suite_lexico() -> None:
    print("\n=== ERROS LÉXICOS ===")

    # LEX-01 — '&' isolado (AFD estado 5: segundo char deve ser '&')
    test_lex(
        "LEX-01  '&' isolado",
        _prog("x : inteiro ; x := 1 & 2"),
    )

    # LEX-02 — '=' isolado (AFD estado 8: '=' sem '=' seguinte e sem '>' anterior)
    test_lex(
        "LEX-02  '=' isolado (use == ou :=)",
        _prog("x : inteiro ; x = 5"),
    )

    # LEX-03 — string não fechada (AFD estado 9: EOF ou \n sem '"' fechando)
    test_lex(
        "LEX-03  string não fechada",
        _prog('msg : caractere ; msg := "sem fechar'),
    )

    # LEX-04 — comentário não fechado (AFD estados 11/12: EOF sem '*/')
    test_lex(
        "LEX-04  comentário não fechado",
        "inicio prog ; /* comentario sem fechar\nx : inteiro ;\nfim",
    )

    # LEX-05 — caractere inválido '@' (não pertence ao alfabeto da linguagem)
    test_lex(
        "LEX-05  caractere inválido '@'",
        _prog("x : inteiro ; x := 5 @ 3"),
    )


# =============================================================================
# ERROS SINTÁTICOS
# =============================================================================

def suite_sintatico() -> None:
    print("\n=== ERROS SINTÁTICOS ===")

    # SIN-01 — falta a palavra reservada 'inicio' no início do programa
    test_syn(
        "SIN-01  falta 'inicio' no início do programa",
        "prog ; x : inteiro ; fim",
    )

    # SIN-02 — falta ';' após o identificador do programa
    test_syn(
        "SIN-02  falta ';' após nome do programa",
        "inicio prog x : inteiro ; fim",
    )

    # SIN-03 — falta 'entao' no comando se
    test_syn(
        "SIN-03  falta 'entao' no se",
        _prog("x : inteiro ; x := 5 ; se x > 3 inicio escreva ( x ) fim"),
    )

    # SIN-04 — falta 'faca' no comando enquanto
    test_syn(
        "SIN-04  falta 'faca' no enquanto",
        _prog("x : inteiro ; x := 1 ; enquanto x <= 10 inicio x := x + 1 fim"),
    )

    # SIN-05 — falta 'inicio' para abrir o bloco de instruções do se
    test_syn(
        "SIN-05  falta 'inicio' no bloco do se",
        _prog("x : inteiro ; x := 5 ; se x > 3 entao escreva ( x ) ; fim"),
    )

    # SIN-06 — declaração dentro de bloco de instruções
    #          instrucao() espera ':=' após id, mas encontra ':'
    test_syn(
        "SIN-06  declaração dentro de bloco de instruções",
        _prog(
            "x : inteiro ; x := 5 ;"
            " se x > 3 entao inicio y : inteiro ; escreva ( x ) fim"
        ),
    )

    # SIN-07 — leia sem parênteses (gramatica exige leia '(' id... ')')
    test_syn(
        "SIN-07  leia sem parênteses",
        _prog("x : inteiro ; leia x"),
    )


# =============================================================================
# ERROS SEMÂNTICOS
# =============================================================================

def suite_semantico() -> None:
    print("\n=== ERROS SEMÂNTICOS ===")

    # SEM-01 — uso de variável não declarada
    test_sem(
        "SEM-01  variável não declarada",
        _prog("x := 5"),
    )

    # SEM-02 — re-declaração da mesma variável no mesmo escopo
    test_sem(
        "SEM-02  re-declaração de variável",
        _prog("x : inteiro ; x : inteiro ; x := 1"),
    )

    # SEM-03 — atribuição incompatível: inteiro := caractere
    test_sem(
        "SEM-03  inteiro := caractere (incompatível)",
        _prog('x : inteiro ; x := "ola"'),
    )

    # SEM-04 — atribuição incompatível: inteiro := logico
    test_sem(
        "SEM-04  inteiro := logico (incompatível)",
        _prog("x : inteiro ; x := verdadeiro"),
    )

    # SEM-05 — atribuição incompatível: inteiro := real
    #          promoção inteiro→real é válida, mas o inverso não
    test_sem(
        "SEM-05  inteiro := real (promoção inversa proibida)",
        _prog("x : inteiro ; r : real ; r := 3.14 ; x := r"),
    )

    # SEM-06 — operador 'not' aplicado a inteiro (exige logico)
    test_sem(
        "SEM-06  'not' sobre inteiro",
        _prog("x : inteiro ; f : logico ; x := 5 ; f := not x"),
    )

    # SEM-07 — operador 'div' com operando real (exige dois inteiros)
    test_sem(
        "SEM-07  'div' com real",
        _prog("x : inteiro ; r : real ; r := 4.0 ; x := 4 div r"),
    )

    # SEM-08 — operador 'mod' com operando real (exige dois inteiros)
    test_sem(
        "SEM-08  'mod' com real",
        _prog("x : inteiro ; r : real ; r := 3.0 ; x := 10 mod r"),
    )

    # SEM-09 — operador '&&' com operandos inteiros (exige logico && logico)
    test_sem(
        "SEM-09  '&&' com inteiros",
        _prog("a : inteiro ; b : inteiro ; f : logico ; a := 1 ; b := 2 ; f := a && b"),
    )

    # SEM-10 — operador 'ou' com operandos inteiros (exige logico ou logico)
    test_sem(
        "SEM-10  'ou' com inteiros",
        _prog("a : inteiro ; b : inteiro ; f : logico ; a := 1 ; b := 0 ; f := a ou b"),
    )

    # SEM-11 — condição do 'se' não é logico (variável inteiro usada como condição)
    test_sem(
        "SEM-11  condição do 'se' não é logico",
        _prog("x : inteiro ; x := 5 ; se x entao inicio escreva ( x ) fim"),
    )

    # SEM-12 — condição do 'enquanto' não é logico
    test_sem(
        "SEM-12  condição do 'enquanto' não é logico",
        _prog("x : inteiro ; x := 1 ; enquanto x faca inicio x := x + 1 fim"),
    )

    # SEM-13 — operador unário '-' sobre logico (exige tipo numérico)
    test_sem(
        "SEM-13  unário '-' sobre logico",
        _prog("f : logico ; x : inteiro ; f := verdadeiro ; x := - f"),
    )

    # SEM-14 — operador relacional '<' entre logicos
    #          (< aceita apenas numérico×numérico ou caractere×caractere)
    test_sem(
        "SEM-14  '<' entre logicos (inválido)",
        _prog(
            "a : logico ; b : logico ; f : logico ;"
            " a := verdadeiro ; b := falso ; f := a < b"
        ),
    )

    # SEM-15 — operador '+' entre logicos (exige numérico ou caractere)
    test_sem(
        "SEM-15  '+' entre logicos (inválido)",
        _prog(
            "a : logico ; b : logico ; f : logico ;"
            " a := verdadeiro ; b := falso ; f := a + b"
        ),
    )


# =============================================================================
# Relatório final
# =============================================================================

def main() -> None:
    suite_valido()
    suite_lexico()
    suite_sintatico()
    suite_semantico()

    total = _pass + _fail
    print(f"\n{'='*55}")
    print(f"Resultado: {_pass}/{total} passaram", end="")
    if _fail:
        print(f"  |  {_fail} falharam")
    else:
        print()
    print('='*55)
    sys.exit(0 if _fail == 0 else 1)


if __name__ == "__main__":
    main()
