import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.error import LexicalError
from src.utils.error import SyntaxError as BRLSyntaxError
from src.lexer.lexer import tokenize_string, tokenize_file
from src.parser.parser import parse_tokens
from src.parser.ast_nodes import print_ast

programa = """
inicio teste;

x : inteiro;
y , z : real;
nome : caractere;
flag : logico;

/* lê o valor de x */
leia(x);
y := 3.14;
z := x + y;

se x >= 10 entao
inicio
    flag := verdadeiro;
    escreva(z)
fim
senao
inicio
    flag := falso;
    escreva("valor menor que 10")
fim;

enquanto x <> 0 faca
inicio
    x := x - 1
fim

fim
"""

try:
    """
    tokens, _ = tokenize_string(programa)
    ast = parse_tokens(tokens)
    print("=== AST do Programa 1 ===")
    print_ast(ast)
    print()
    """

    tokens2, _ = tokenize_file("tests/exemplo.LC")
    ast2 = parse_tokens(tokens2)
    print("=== AST do Programa 2 ===")
    print_ast(ast2)
except LexicalError as e:
    print(e)
except BRLSyntaxError as e:
    print(e)
