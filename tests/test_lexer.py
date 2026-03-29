import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.error import LexicalError
from src.lexer.lexer import tokenize_file, tokenize_string

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
    tokens, ts = tokenize_string(programa)
    print("=== TOKENS do Progama 1 ===")
    for tok in tokens:
        print(f"  {tok}")
    print()
    print("=== TABELA DE SÍMBOLOS do Progama 1 ===")
    print(ts)
    """
    
    tokens2, ts2 = tokenize_file("tests/exemplo.LC")
    print("=== TOKENS do Progama 2 ===")
    for tok in tokens2:
        print(f"  {tok}")
    print()
    print("=== TABELA DE SÍMBOLOS do Progama 2 ===")
    print(ts2)
except LexicalError as e:
    print(e)
