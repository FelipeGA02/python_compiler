class Token:
    def __init__(self, tipo, lexema, linha, coluna):
        self.tipo = tipo      
        self.lexema = lexema   
        self.linha = linha     
        self.coluna = coluna   

    def __repr__(self):
        return f"Token(tipo={self.tipo}, lexema='{self.lexema}', linha={self.linha}, coluna={self.coluna})"