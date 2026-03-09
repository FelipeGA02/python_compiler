from lexer.token_types import TokenType, RESERVED_WORDS
from lexer.token import Token

lexema = "inteiro"

if lexema in RESERVED_WORDS:
    tipo = RESERVED_WORDS[lexema]
else:
    tipo = TokenType.ID