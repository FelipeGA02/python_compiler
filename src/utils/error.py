class LexicalError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[Erro léxico] linha {line}, col {col}: {msg}")
        self.line = line
        self.col  = col


class SyntaxError(Exception):
    def __init__(self, msg, line: int = 0, col: int = 0):
        loc = f" linha {line}, col {col}" if line else ""
        super().__init__(f"[Erro sintático]{loc}: {msg}")
        self.line = line
        self.col  = col


class SemanticError(Exception):
    def __init__(self, msg, line: int = 0, col: int = 0):
        loc = f" linha {line}, col {col}" if line else ""
        super().__init__(f"[Erro semântico]{loc}: {msg}")
        self.line = line
        self.col  = col
