"""
    Felipe Gurgel Araujo - D21120
    Compilador BRL — pipeline: Léxico → Sintático → Semântico
"""

import sys
import argparse

from src.lexer.lexer import tokenize_string
from src.parser.parser import parse_tokens
from src.parser.ast_nodes import print_ast
from src.semantic.semantic_analyzer import analyze
from src.utils.error import LexicalError
from src.utils.error import SyntaxError as BRLSyntaxError
from src.utils.error import SemanticError


def _run(source: str, verbose: bool = False) -> bool:
    """Executa todas as fases e devolve True se bem-sucedido."""

    # ── Fase 1: Análise Léxica ────────────────────────────────────────────────
    try:
        tokens, symbol_table = tokenize_string(source)
    except LexicalError as e:
        print(e)
        return False

    if verbose:
        print("=== TOKENS ===")
        for tok in tokens:
            print(f"  {tok}")
        print()
        print("=== TABELA DE SÍMBOLOS (léxico) ===")
        print(symbol_table)
        print()

    # ── Fase 2: Análise Sintática ─────────────────────────────────────────────
    try:
        ast = parse_tokens(tokens)
    except BRLSyntaxError as e:
        print(e)
        return False

    if verbose:
        print("=== AST ===")
        print_ast(ast)
        print()

    # ── Fase 3: Análise Semântica ─────────────────────────────────────────────
    try:
        tipo_vars = analyze(ast)
    except SemanticError as e:
        print(e)
        return False

    if verbose:
        print("=== VARIÁVEIS DECLARADAS ===")
        for name, tipo in tipo_vars.items():
            print(f"  {name}: {tipo}")
        print()

    print("OK — programa aceito.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Compilador BRL")
    parser.add_argument("arquivo", nargs="?", help="arquivo fonte .LC")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="exibe tokens, AST e tabela de variáveis")
    args = parser.parse_args()

    if args.arquivo:
        try:
            with open(args.arquivo, encoding="utf-8") as f:
                source = f.read()
        except OSError as e:
            print(f"Erro ao abrir arquivo: {e}")
            sys.exit(1)
    else:
        # Programa de demonstração embutido (traço da especificação)
        source = """
            inicio prog ;
                x : inteiro ;
                x := 10 ;
                escreva ( x )
            fim
        """

    ok = _run(source, verbose=args.verbose)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
