class Symbol:
    def __init__(self, name, token, lexeme, classNumber=None, type=None, memAddress=None):
        self.name = name
        self.token = token
        self.lexeme = lexeme
        self.classNumber = classNumber
        self.type = type
        self.memAddress = memAddress

    def __repr__(self):
        return f"Symbol(name={self.name}, token={self.token}, lexeme={self.lexeme}, type={self.type})"

class SymbolTable:
    def __init__(self):
        self.table = {}

    def searchLexeme(self, lexeme):
        return self.table.get(lexeme)

    def insertToken(self, lexeme, token, classNumber=None, type=None, memAddress=None):

        if lexeme in self.table:
            return self.table[lexeme]

        symbol = Symbol(
            name=lexeme,
            token=token,
            lexeme=lexeme,
            classNumber=classNumber,
            type=type,
            memAddress=memAddress   
        )

        self.table[lexeme] = symbol
        return symbol