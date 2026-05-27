"""
    Felipe Gurgel Araujo - D21120
    Compilador BRL — pipeline: Léxico → Sintático → Semântico
"""

import sys
import argparse

from src.lexer.lexer import tokenize_string
from src.parser.parser import parse_tokens
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
        _print_ast(ast)
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


def _print_ast(node, indent: int = 0) -> None:
    prefix = "  " * indent
    if isinstance(node, list):
        for item in node:
            _print_ast(item, indent)
        return
    from src.parser.ast_nodes import (
        Program, VarDecl, Assign, If, While, Read, Write,
        BinOp, UnaryOp, Var, IntConst, RealConst, StringConst, BoolConst,
    )
    if isinstance(node, Program):
        print(f"{prefix}Programa '{node.name}'")
        for d in node.decls:
            _print_ast(d, indent + 1)
        for s in node.stmts:
            _print_ast(s, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}Decl {', '.join(node.names)} : {node.type}")
    elif isinstance(node, Assign):
        print(f"{prefix}Atrib {node.name} :=")
        _print_ast(node.expr, indent + 2)
    elif isinstance(node, If):
        print(f"{prefix}Se")
        _print_ast(node.cond, indent + 2)
        print(f"{prefix}  Entao")
        for s in node.then_stmts:
            _print_ast(s, indent + 2)
        if node.else_stmts:
            print(f"{prefix}  Senao")
            for s in node.else_stmts:
                _print_ast(s, indent + 2)
    elif isinstance(node, While):
        print(f"{prefix}Enquanto")
        _print_ast(node.cond, indent + 2)
        print(f"{prefix}  Faca")
        for s in node.body:
            _print_ast(s, indent + 2)
    elif isinstance(node, Read):
        print(f"{prefix}Leia({', '.join(node.names)})")
    elif isinstance(node, Write):
        print(f"{prefix}Escreva")
        _print_ast(node.expr, indent + 2)
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp '{node.op}'")
        _print_ast(node.left, indent + 2)
        _print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnOp '{node.op}'")
        _print_ast(node.operand, indent + 2)
    elif isinstance(node, Var):
        print(f"{prefix}Var '{node.name}'")
    elif isinstance(node, IntConst):
        print(f"{prefix}Int {node.value}")
    elif isinstance(node, RealConst):
        print(f"{prefix}Real {node.value}")
    elif isinstance(node, StringConst):
        print(f"{prefix}Str '{node.value}'")
    elif isinstance(node, BoolConst):
        print(f"{prefix}Bool {'verdadeiro' if node.value else 'falso'}")
    else:
        print(f"{prefix}{node!r}")


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
