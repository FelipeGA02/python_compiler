from src.utils.symbol_table import Symbol, SymbolTable
from src.utils.error import LexicalError
from src.lexer.token import Token, TokenType, RESERVED_WORDS

class Lexer:
    """
        AFD com os seguintes estados:

        Estados intermediários (não-finais):
        0   inicial
        1   lendo letra/_ (identificador ou reservada)
        2   lendo dígitos inteiros
        3   viu ponto após dígitos (parte fracionária)
        4   lendo dígitos da fração
        5   viu primeiro '&'
        6   viu ':'
        7   viu '<'
        8   viu '>' ou primeiro '='
        9   dentro de string (consumindo chars)
        10  viu '/' (pode ser DIV ou início de comentário)
        11  dentro de comentário /* ... */
        12  viu '*' dentro de comentário (possível fechamento)

        Estados finais (aceitação + emissão, retornam a q0):
        13  ID / palavra reservada
        14  CONST_INT
        15  CONST_REAL
        16  token simples de 1 char  ( + - * ( ) , ; )
        17  &&
        18  :=
        19  :
        20  <  <=  <>
        21  >  >=  ==
        22  CONST_STRING
        23  / (DIV)
        24  comentário (descartado)
    """

    # Tokens de 1 caractere emitidos diretamente em q0 (estado final q16)
    _SIMPLE_TOKENS = {
        '+': TokenType.MAIS,
        '-': TokenType.MENOS,
        '*': TokenType.MULT,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        ',': TokenType.VIRGULA,
        ';': TokenType.PONTO_VIRGULA,
    }

    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0
        self.line    = 1
        self.col     = 1
        self.tokens: list[Token] = []
        self.ts      = SymbolTable()

    def _peek(self) -> str | None:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]

    def _advance(self) -> str | None:
        ch = self._peek()
        if ch is not None:
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
        return ch

    def _back(self):
        """Devolve um caractere ao stream (retrocede 1 posição)."""
        if self.pos > 0:
            self.pos -= 1
            if self.source[self.pos] == '\n':
                self.line -= 1
                prev_nl = self.source.rfind('\n', 0, self.pos)
                self.col = self.pos - prev_nl
            else:
                self.col -= 1

    def _emit(self, lexeme: str, token_type: TokenType) -> Token:
        tok = Token(token_type, lexeme, self.line, self.col)
        self.tokens.append(tok)
        if token_type in (TokenType.ID, TokenType.CONST_INT,
                          TokenType.CONST_REAL, TokenType.CONST_STRING,
                          TokenType.CONST_BOOL) or token_type in RESERVED_WORDS.values():
            self.ts.insertToken(lexeme, token_type)
        return tok

    def tokenize(self) -> list[Token]:
        estado = 0
        lexema = ""

        while True:
            b = self._advance()   # lê próximo caractere (lookahead)

            # ── q0: estado inicial ────────────────────────────────────
            if estado == 0:
                if b is None:
                    self._emit("EOF", TokenType.EOF)
                    break

                # descarta espaço em branco
                if b in (' ', '\t', '\n', '\r'):
                    continue

                # início de identificador ou palavra reservada → q1
                elif b.isalpha() or b == '_':
                    lexema = b
                    estado = 1

                # operadores aditivos + e - (sempre operadores, nunca sinal) → q16*
                elif b in ('+', '-'):
                    self._emit(b, self._SIMPLE_TOKENS[b])

                # constante inteira ou real sem sinal → q2
                elif b.isdigit():
                    lexema = b
                    estado = 2

                # constante string → q9
                elif b == '"':
                    lexema = b
                    estado = 9

                # operador && (primeiro '&') → q5
                elif b == '&':
                    lexema = b
                    estado = 5

                # atribuição := ou dois-pontos : → q6
                elif b == ':':
                    lexema = b
                    estado = 6

                # relacionais < <= <> → q7
                elif b == '<':
                    lexema = b
                    estado = 7

                # relacionais > >=  ou  == → q8
                elif b == '>':
                    lexema = b
                    estado = 8

                elif b == '=':
                    lexema = b
                    estado = 8

                # divisão ou início de comentário → q10
                elif b == '/':
                    lexema = b
                    estado = 10

                # tokens simples de 1 char → q16*
                elif b in self._SIMPLE_TOKENS:
                    self._emit(b, self._SIMPLE_TOKENS[b])

                else:
                    raise LexicalError(
                        f"caractere inesperado {b!r}", self.line, self.col)

            # ── q1: lendo ID / palavra reservada ─────────────────────
            elif estado == 1:
                if b is not None and (b.isalpha() or b.isdigit() or b == '_'):
                    lexema += b
                else:
                    if b is not None:
                        self._back()
                    # q13*: emite ID ou palavra reservada
                    tok_type = RESERVED_WORDS.get(lexema, TokenType.ID)
                    if tok_type in (TokenType.VERDADEIRO, TokenType.FALSO):
                        tok_type = TokenType.CONST_BOOL
                    self._emit(lexema, tok_type)
                    lexema = ""
                    estado = 0

            # ── q2: lendo dígitos inteiros ────────────────────────────
            elif estado == 2:
                if b is not None and b.isdigit():
                    lexema += b
                elif b == '.':
                    next_ch = self._peek()
                    if next_ch is not None and next_ch.isdigit():
                        lexema += b
                        estado = 3           # → q3 (viu ponto)
                    else:
                        self._back()
                        # q14*: emite CONST_INT
                        self._emit(lexema, TokenType.CONST_INT)
                        lexema = ""
                        estado = 0
                else:
                    if b is not None:
                        self._back()
                    # q14*: emite CONST_INT
                    self._emit(lexema, TokenType.CONST_INT)
                    lexema = ""
                    estado = 0

            # ── q3: viu ponto — aguarda dígito da fração ─────────────
            elif estado == 3:
                if b is not None and b.isdigit():
                    lexema += b
                    estado = 4               # → q4 (lendo fração)
                else:
                    raise LexicalError(
                        f"real mal formado: {lexema!r}", self.line, self.col)

            # ── q4: lendo dígitos da fração ───────────────────────────
            elif estado == 4:
                if b is not None and b.isdigit():
                    lexema += b
                else:
                    if b is not None:
                        self._back()
                    # q15*: emite CONST_REAL
                    self._emit(lexema, TokenType.CONST_REAL)
                    lexema = ""
                    estado = 0

            # ── q5: viu primeiro '&' ──────────────────────────────────
            elif estado == 5:
                if b == '&':
                    lexema += b
                    # q17*: emite &&
                    self._emit(lexema, TokenType.AND)
                    lexema = ""
                    estado = 0
                else:
                    raise LexicalError(
                        f"'&' isolado inválido", self.line, self.col)

            # ── q6: viu ':' ───────────────────────────────────────────
            elif estado == 6:
                if b == '=':
                    lexema += b
                    # q18*: emite :=
                    self._emit(lexema, TokenType.ATRIBUICAO)
                else:
                    if b is not None:
                        self._back()
                    # q19*: emite :
                    self._emit(lexema, TokenType.DOIS_PONTOS)
                lexema = ""
                estado = 0

            # ── q7: viu '<' ───────────────────────────────────────────
            elif estado == 7:
                if b == '=':
                    lexema += b
                    self._emit(lexema, TokenType.MENOR_IGUAL)
                elif b == '>':
                    lexema += b
                    self._emit(lexema, TokenType.DIFERENTE)
                else:
                    if b is not None:
                        self._back()
                    # q20*: emite <
                    self._emit(lexema, TokenType.MENOR)
                lexema = ""
                estado = 0

            # ── q8: viu '>' ou primeiro '=' ───────────────────────────
            elif estado == 8:
                if b == '=':
                    lexema += b
                    # q21*: >= ou ==
                    if lexema == '>=':
                        self._emit(lexema, TokenType.MAIOR_IGUAL)
                    else:
                        self._emit(lexema, TokenType.IGUAL)
                else:
                    if b is not None:
                        self._back()
                    if lexema == '>':
                        # q21*: emite >
                        self._emit(lexema, TokenType.MAIOR)
                    else:
                        raise LexicalError(
                            f"'=' isolado inválido (use == ou :=)",
                            self.line, self.col)
                lexema = ""
                estado = 0

            # ── q9: dentro de string ──────────────────────────────────
            elif estado == 9:
                if b is None or b in ('\n', '\r'):
                    raise LexicalError(
                        "string não fechada", self.line, self.col)
                elif b == '"':
                    lexema += b
                    # q22*: emite CONST_STRING
                    self._emit(lexema, TokenType.CONST_STRING)
                    lexema = ""
                    estado = 0
                else:
                    lexema += b

            # ── q10: viu '/' ──────────────────────────────────────────
            elif estado == 10:
                if b == '*':
                    # início de comentário /* ... */ → q11
                    lexema = ""
                    estado = 11
                else:
                    if b is not None:
                        self._back()
                    # q23*: emite DIV
                    self._emit("/", TokenType.DIV)
                    lexema = ""
                    estado = 0

            # ── q11: dentro de comentário ─────────────────────────────
            elif estado == 11:
                if b is None:
                    raise LexicalError(
                        "comentário não fechado", self.line, self.col)
                elif b == '*':
                    estado = 12              # → q12 (possível fechamento)

            # ── q12: viu '*' dentro de comentário ────────────────────
            elif estado == 12:
                if b is None:
                    raise LexicalError(
                        "comentário não fechado", self.line, self.col)
                elif b == '/':
                    # q24*: comentário encerrado — descarta
                    estado = 0
                elif b == '*':
                    pass                     # permanece em q12
                else:
                    estado = 11              # volta a consumir o comentário

        return self.tokens


def tokenize_file(path: str) -> tuple[list[Token], SymbolTable]:
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    return tokens, lexer.ts


def tokenize_string(source: str) -> tuple[list[Token], SymbolTable]:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    return tokens, lexer.ts
