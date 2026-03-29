class LexicalError(Exception):
    def __init__(self, msg, line, col):
        super().__init__(f"[Erro léxico] linha {line}, col {col}: {msg}")
        self.line = line
        self.col  = col