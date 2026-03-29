from src.utils.symbol_table import Symbol, SymbolTable
from src.utils.error import LexicalError
from src.lexer.token import Token, TokenType, RESERVED_WORDS

class Lexer:
    """
    AFD com os seguintes estados:
      0        – inicial
      1        – lendo letra/_ (identificador ou reservada)
      3        – viu + ou - (pode ser sinal de constante ou operador)
      4        – lendo dígitos inteiros
      6        – viu ponto após dígitos (parte fracionária)
      7        – lendo dígitos da fração
      11       – viu primeiro '&'
      13       – viu ':'
      16       – viu '<'
      18       – viu '>' ou primeiro '='
      20       – dentro de string (consumindo chars)
      22       – viu '/' (pode ser DIV ou início de comentário)
      23       – dentro de comentário /* ... */
      23b/'*'  – viu '*' dentro de comentário (possível fechamento)
 
    Estados finais (emitem token ao sair):
      2  – ID / palavra reservada
      5  – CONST_INT
      8  – CONST_REAL
      10 – token simples de 1 char ( + - * / ( ) , ; )
      12 – &&
      14 – :=
      15 – :
      17 – <  <=  <>
      19 – >  >=  ==
      21 – CONST_STRING
      24 – comentário (descartado)
    """
 
    # Mapeamento de tokens simples (1 char, exceto '/' que precisa lookahead)
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
        tok = Token(token_type, lexeme)
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
            b = self._advance() # loockahead
 
            # ── q0: estado inicial ────────────────────────────────────
            if estado == 0:
                if b is None:
                    self._emit("EOF", TokenType.EOF)
                    break
 
                # descarta espaço em branco
                if b in (' ', '\t', '\n', '\r'):
                    continue
 
                # início de identificador ou palavra reservada
                elif b.isalpha() or b == '_':
                    lexema = b
                    estado = 1
 
                # sinal de constante numérica ou operador aditivo
                elif b in ('+', '-'):
                    next_ch = self._peek()
                    if next_ch is not None and next_ch.isdigit():
                        lexema = b
                        estado = 3
                    else:
                        self._emit(b, self._SIMPLE_TOKENS[b])
 
                # constante inteira ou real sem sinal
                elif b.isdigit():
                    lexema = b
                    estado = 4
 
                # constante string
                elif b == '"':
                    lexema = b
                    estado = 20
 
                # operador && (primeiro &)
                elif b == '&':
                    lexema = b
                    estado = 11
 
                # atribuição := ou dois-pontos :
                elif b == ':':
                    lexema = b
                    estado = 13
 
                # relacionais < <= <>
                elif b == '<':
                    lexema = b
                    estado = 16
 
                # relacionais > >=  ou  ==
                elif b == '>':
                    lexema = b
                    estado = 18
 
                elif b == '=':
                    lexema = b
                    estado = 18
 
                # divisão ou início de comentário
                elif b == '/':
                    lexema = b
                    estado = 22
 
                # tokens simples de 1 char
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
                    # devolve o caractere que não faz parte do lexema
                    if b is not None:
                        self._back()
                    # q2*: emite ID ou palavra reservada
                    tok_type = RESERVED_WORDS.get(lexema, TokenType.ID)
                    # verdadeiro / falso → CONST_BOOL
                    if tok_type in (TokenType.VERDADEIRO, TokenType.FALSO):
                        tok_type = TokenType.CONST_BOOL
                    self._emit(lexema, tok_type)
                    lexema = ""
                    estado = 0
 
            # ── q3: viu sinal + ou - antes de dígito ─────────────────
            elif estado == 3:
                if b is not None and b.isdigit():
                    lexema += b
                    estado = 4
                else:
                    # era operador simples, não sinal
                    op = lexema[0]
                    self._emit(op, self._SIMPLE_TOKENS[op])
                    lexema = ""
                    if b is not None:
                        self._back()
                    estado = 0
 
            # ── q4: lendo dígitos inteiros ────────────────────────────
            elif estado == 4:
                if b is not None and b.isdigit():
                    lexema += b
                elif b == '.':
                    # verifica se próximo char é dígito (real) ou outro
                    next_ch = self._peek()
                    if next_ch is not None and next_ch.isdigit():
                        lexema += b
                        estado = 6
                    else:
                        # ponto não pertence ao número
                        self._back()
                        # q5*: emite CONST_INT
                        self._emit(lexema, TokenType.CONST_INT)
                        lexema = ""
                        estado = 0
                else:
                    if b is not None:
                        self._back()
                    # q5*: emite CONST_INT
                    self._emit(lexema, TokenType.CONST_INT)
                    lexema = ""
                    estado = 0
 
            # ── q6: viu ponto — aguarda dígito da fração ─────────────
            elif estado == 6:
                if b is not None and b.isdigit():
                    lexema += b
                    estado = 7
                else:
                    raise LexicalError(
                        f"real mal formado: {lexema!r}", self.line, self.col)
 
            # ── q7: lendo dígitos da fração ───────────────────────────
            elif estado == 7:
                if b is not None and b.isdigit():
                    lexema += b
                else:
                    if b is not None:
                        self._back()
                    # q8*: emite CONST_REAL
                    self._emit(lexema, TokenType.CONST_REAL)
                    lexema = ""
                    estado = 0
 
            # ── q11: viu primeiro '&' ─────────────────────────────────
            elif estado == 11:
                if b == '&':
                    lexema += b
                    # q12*: emite &&
                    self._emit(lexema, TokenType.AND)
                    lexema = ""
                    estado = 0
                else:
                    raise LexicalError(
                        f"'&' isolado inválido", self.line, self.col)
 
            # ── q13: viu ':' ──────────────────────────────────────────
            elif estado == 13:
                if b == '=':
                    lexema += b
                    # q14*: emite :=
                    self._emit(lexema, TokenType.ATRIBUICAO)
                else:
                    if b is not None:
                        self._back()
                    # q15*: emite :
                    self._emit(lexema, TokenType.DOIS_PONTOS)
                lexema = ""
                estado = 0
 
            # ── q16: viu '<' ──────────────────────────────────────────
            elif estado == 16:
                if b == '=':
                    lexema += b
                    self._emit(lexema, TokenType.MENOR_IGUAL)
                elif b == '>':
                    lexema += b
                    self._emit(lexema, TokenType.DIFERENTE)
                else:
                    if b is not None:
                        self._back()
                    # q17*: emite <
                    self._emit(lexema, TokenType.MENOR)
                lexema = ""
                estado = 0
 
            # ── q18: viu '>' ou primeiro '=' ─────────────────────────
            elif estado == 18:
                if b == '=':
                    lexema += b
                    # >= ou ==
                    if lexema == '>=':
                        self._emit(lexema, TokenType.MAIOR_IGUAL)
                    else:
                        self._emit(lexema, TokenType.IGUAL)
                else:
                    if b is not None:
                        self._back()
                    if lexema == '>':
                        self._emit(lexema, TokenType.MAIOR)
                    else:
                        raise LexicalError(
                            f"'=' isolado inválido (use == ou :=)",
                            self.line, self.col)
                lexema = ""
                estado = 0
 
            # ── q20: dentro de string ─────────────────────────────────
            elif estado == 20:
                if b is None or b in ('\n', '\r'):
                    raise LexicalError(
                        "string não fechada", self.line, self.col)
                elif b == '"':
                    lexema += b
                    # q21*: emite CONST_STRING
                    self._emit(lexema, TokenType.CONST_STRING)
                    lexema = ""
                    estado = 0
                else:
                    lexema += b
 
            # ── q22: viu '/' ──────────────────────────────────────────
            elif estado == 22:
                if b == '*':
                    # início de comentário /* ... */
                    lexema = ""
                    estado = 23
                else:
                    if b is not None:
                        self._back()
                    # q10*: emite DIV
                    self._emit("/", TokenType.DIV)
                    lexema = ""
                    estado = 0
 
            # ── q23: dentro de comentário ─────────────────────────────
            elif estado == 23:
                if b is None:
                    raise LexicalError(
                        "comentário não fechado", self.line, self.col)
                elif b == '*':
                    estado = '23b'   # possível fechamento
 
            # ── q23b: viu '*' dentro de comentário ───────────────────
            elif estado == '23b':
                if b is None:
                    raise LexicalError(
                        "comentário não fechado", self.line, self.col)
                elif b == '/':
                    # q24*: comentário encerrado — descarta
                    estado = 0
                elif b == '*':
                    pass             # continua em 23b
                else:
                    estado = 23      # volta a consumir o comentário
 
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
    