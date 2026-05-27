from enum import Enum

class Token:
    def __init__(self, type, lexeme, line: int = 0, col: int = 0):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, linha={self.line})"
class TokenType(Enum):
    ID = "ID"

    CONST_INT = "CONST_INT"
    CONST_REAL = "CONST_REAL"
    CONST_STRING = "CONST_STRING"
    CONST_BOOL = "CONST_BOOL"

    INTEIRO = "inteiro"
    REAL = "real"
    LOGICO = "logico"
    CARACTERE = "caractere"

    SE = "se"
    SENAO = "senao"
    ENQUANTO = "enquanto"
    FACA = "faca"
    ENTAO   = "entao"

    LEIA = "leia"
    ESCREVA = "escreva"

    INICIO = "inicio"
    FIM = "fim"

    VERDADEIRO = "verdadeiro"
    FALSO = "falso"

    IGUAL = "=="
    DIFERENTE = "<>"
    MENOR = "<"
    MAIOR = ">"
    MENOR_IGUAL = "<="
    MAIOR_IGUAL = ">="

    MAIS = "+"
    MENOS = "-"
    MULT = "*"
    DIV = "/"
    DIV_INT = "div"
    MOD = "mod"

    AND = "&&"
    OR = "ou"
    NOT = "not"

    ATRIBUICAO = ":="

    LPAREN = "("
    RPAREN = ")"
    VIRGULA = ","
    PONTO_VIRGULA = ";"
    DOIS_PONTOS = ":"

    EOF = "EOF"

RESERVED_WORDS = {
    "inteiro": TokenType.INTEIRO,
    "real": TokenType.REAL,
    "logico": TokenType.LOGICO,
    "caractere": TokenType.CARACTERE,

    "se": TokenType.SE,
    "senao": TokenType.SENAO,
    "enquanto": TokenType.ENQUANTO,
    "faca": TokenType.FACA,
    "entao": TokenType.ENTAO,

    "leia": TokenType.LEIA,
    "escreva": TokenType.ESCREVA,

    "inicio": TokenType.INICIO,
    "fim": TokenType.FIM,

    "verdadeiro": TokenType.VERDADEIRO,
    "falso": TokenType.FALSO,

    "div": TokenType.DIV_INT,
    "mod": TokenType.MOD,
    "ou": TokenType.OR,
    "not": TokenType.NOT,
}