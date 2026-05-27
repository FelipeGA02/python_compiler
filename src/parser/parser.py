"""
Analisador Sintático LL(1) para a linguagem BRL — descida recursiva top-down.

Primitivas do parser preditivo:
  tok           — token de lookahead corrente
  consome()     — avança para o próximo token
  casar(t)      — se tok == t: consome(); senão: erroSintatico()
  erroSintatico() — relata erro e encerra

Uma função por não-terminal; o switch(tok) reproduz as linhas da tabela LL(1).
Cada caso escolhido = produção aplicada; o default = célula vazia = erro.
"""
from __future__ import annotations
from typing import List, Optional, Tuple, Any

from src.lexer.token import Token, TokenType
from src.parser.ast_nodes import (
    Program, VarDecl, Assign, If, While, Read, Write,
    BinOp, UnaryOp, Var, IntConst, RealConst, StringConst, BoolConst,
)
from src.utils.error import SyntaxError as BRLSyntaxError


class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        # tok = lookahead corrente, inicializado com o primeiro token
        self.tok: Token = tokens[0] if tokens else Token(TokenType.EOF, 'EOF')

    # =========================================================================
    # Primitivas
    # =========================================================================

    def consome(self) -> Token:
        """Avança para o próximo token e devolve o consumido."""
        atual = self.tok
        self.pos += 1
        self.tok = (
            self.tokens[self.pos]
            if self.pos < len(self.tokens)
            else self.tokens[-1]   # permanece no EOF
        )
        return atual

    def casar(self, esperado: TokenType) -> Token:
        """Se tok == esperado: consome e devolve o token. Senão: erroSintatico."""
        if self.tok.type != esperado:
            raise BRLSyntaxError(
                f"esperado '{esperado.value}', encontrado '{self.tok.lexeme}'",
                self.tok.line, self.tok.col,
            )
        return self.consome()

    def erroSintatico(self, msg: str = "") -> None:
        extra = f": {msg}" if msg else ""
        raise BRLSyntaxError(
            f"token inesperado '{self.tok.lexeme}'{extra}",
            self.tok.line, self.tok.col,
        )

    # =========================================================================
    # Ponto de entrada
    # =========================================================================

    def parse(self) -> Program:
        """tok já foi inicializado em __init__; invoca o símbolo inicial."""
        return self.programa()

    # =========================================================================
    # <programa> → inicio id ; <corpo> fim $
    # =========================================================================

    def programa(self) -> Program:
        self.casar(TokenType.INICIO)
        name_tok = self.casar(TokenType.ID)
        self.casar(TokenType.PONTO_VIRGULA)
        decls, stmts = self.corpo()
        self.casar(TokenType.FIM)
        self.casar(TokenType.EOF)          # entrada deve terminar aqui
        return Program(name=name_tok.lexeme, decls=decls, stmts=stmts)

    # =========================================================================
    # <corpo> — declarações seguidas de instruções
    # FOLLOW(corpo) = {fim}
    # =========================================================================

    def corpo(self) -> Tuple[List[VarDecl], List[Any]]:
        tt = self.tok.type

        if tt == TokenType.ID:
            id_tok = self.casar(TokenType.ID)
            return self.apos_id(id_tok)

        elif tt == TokenType.SE:
            self.casar(TokenType.SE)
            node = self.se_resto()
            rest = self.resto_inst()
            return [], [node] + rest

        elif tt == TokenType.ENQUANTO:
            self.casar(TokenType.ENQUANTO)
            node = self.enq_resto()
            rest = self.resto_inst()
            return [], [node] + rest

        elif tt == TokenType.LEIA:
            tok = self.casar(TokenType.LEIA)
            node = self.leia_args(tok.line)
            rest = self.resto_inst()
            return [], [node] + rest

        elif tt == TokenType.ESCREVA:
            tok = self.casar(TokenType.ESCREVA)
            node = self.esc_args(tok.line)
            rest = self.resto_inst()
            return [], [node] + rest

        elif tt == TokenType.FIM:
            return [], []              # ε — FOLLOW(corpo) = {fim}

        else:
            self.erroSintatico("início de corpo/instrução esperado")

    # =========================================================================
    # <apos_id> — decide declaração (','/':') ou atribuição (':=')
    # =========================================================================

    def apos_id(self, id_tok: Token) -> Tuple[List[VarDecl], List[Any]]:
        tt = self.tok.type

        if tt in (TokenType.VIRGULA, TokenType.DOIS_PONTOS):
            # declaração: <ids_resto> : <tipo> ; <corpo>
            names = self.ids_resto([id_tok.lexeme])
            self.casar(TokenType.DOIS_PONTOS)
            tipo  = self.tipo()
            self.casar(TokenType.PONTO_VIRGULA)
            decl = VarDecl(names=names, type=tipo)
            more_decls, stmts = self.corpo()
            return [decl] + more_decls, stmts

        elif tt == TokenType.ATRIBUICAO:
            # atribuição: := <exp> <resto_inst>
            self.casar(TokenType.ATRIBUICAO)
            expr = self.exp()
            rest = self.resto_inst()
            return [], [Assign(name=id_tok.lexeme, expr=expr, line=id_tok.line)] + rest

        else:
            self.erroSintatico("esperado ':=', ',' ou ':'")

    # =========================================================================
    # <ids_resto> → , id <ids_resto> | ε       FOLLOW = {':'}
    # =========================================================================

    def ids_resto(self, names: List[str]) -> List[str]:
        if self.tok.type == TokenType.VIRGULA:
            self.casar(TokenType.VIRGULA)
            tok = self.casar(TokenType.ID)
            names.append(tok.lexeme)
            return self.ids_resto(names)
        return names    # ε

    # =========================================================================
    # <tipo> → inteiro | real | logico | caractere
    # =========================================================================

    def tipo(self) -> str:
        tt = self.tok.type
        if tt == TokenType.INTEIRO:
            self.casar(TokenType.INTEIRO)
            return 'inteiro'
        elif tt == TokenType.REAL:
            self.casar(TokenType.REAL)
            return 'real'
        elif tt == TokenType.LOGICO:
            self.casar(TokenType.LOGICO)
            return 'logico'
        elif tt == TokenType.CARACTERE:
            self.casar(TokenType.CARACTERE)
            return 'caractere'
        else:
            self.erroSintatico("tipo esperado (inteiro | real | logico | caractere)")

    # =========================================================================
    # <resto_inst> → ; <instrucao> <resto_inst> | ε      FOLLOW = {fim}
    # =========================================================================

    def resto_inst(self) -> List[Any]:
        if self.tok.type == TokenType.PONTO_VIRGULA:
            self.casar(TokenType.PONTO_VIRGULA)
            stmt = self.instrucao()
            rest = self.resto_inst()
            return [stmt] + rest
        return []       # ε

    # =========================================================================
    # <instrucao>
    # =========================================================================

    def instrucao(self) -> Any:
        tt = self.tok.type

        if tt == TokenType.ID:
            id_tok = self.casar(TokenType.ID)
            self.casar(TokenType.ATRIBUICAO)
            expr = self.exp()
            return Assign(name=id_tok.lexeme, expr=expr, line=id_tok.line)

        elif tt == TokenType.SE:
            tok = self.casar(TokenType.SE)
            node = self.se_resto()
            node.line = tok.line
            return node

        elif tt == TokenType.ENQUANTO:
            tok = self.casar(TokenType.ENQUANTO)
            node = self.enq_resto()
            node.line = tok.line
            return node

        elif tt == TokenType.LEIA:
            tok = self.casar(TokenType.LEIA)
            return self.leia_args(tok.line)

        elif tt == TokenType.ESCREVA:
            tok = self.casar(TokenType.ESCREVA)
            return self.esc_args(tok.line)

        else:
            self.erroSintatico("instrução esperada")

    # =========================================================================
    # <se_resto> → <exp> entao inicio <lista_inst> fim <senao_opt>
    # <senao_opt> → senao inicio <lista_inst> fim | ε     FOLLOW = {';', fim}
    # =========================================================================

    def se_resto(self) -> If:
        cond       = self.exp()
        self.casar(TokenType.ENTAO)
        self.casar(TokenType.INICIO)
        then_stmts = self.lista_inst()
        self.casar(TokenType.FIM)
        else_stmts = self.senao_opt()
        return If(cond=cond, then_stmts=then_stmts, else_stmts=else_stmts)

    def senao_opt(self) -> Optional[List[Any]]:
        if self.tok.type == TokenType.SENAO:
            self.casar(TokenType.SENAO)
            self.casar(TokenType.INICIO)
            stmts = self.lista_inst()
            self.casar(TokenType.FIM)
            return stmts
        return None     # ε

    # =========================================================================
    # <enq_resto> → <exp> faca inicio <lista_inst> fim
    # =========================================================================

    def enq_resto(self) -> While:
        cond = self.exp()
        self.casar(TokenType.FACA)
        self.casar(TokenType.INICIO)
        body = self.lista_inst()
        self.casar(TokenType.FIM)
        return While(cond=cond, body=body)

    # =========================================================================
    # <leia_args> → ( id <leia_ids> )
    # <leia_ids>  → , id <leia_ids> | ε        FOLLOW = {')'}
    # =========================================================================

    def leia_args(self, line: int = 0) -> Read:
        self.casar(TokenType.LPAREN)
        tok   = self.casar(TokenType.ID)
        names = self.leia_ids([tok.lexeme])
        self.casar(TokenType.RPAREN)
        return Read(names=names, line=line)

    def leia_ids(self, names: List[str]) -> List[str]:
        if self.tok.type == TokenType.VIRGULA:
            self.casar(TokenType.VIRGULA)
            tok = self.casar(TokenType.ID)
            names.append(tok.lexeme)
            return self.leia_ids(names)
        return names    # ε

    # =========================================================================
    # <esc_args> → ( <exp> )
    # =========================================================================

    def esc_args(self, line: int = 0) -> Write:
        self.casar(TokenType.LPAREN)
        expr = self.exp()
        self.casar(TokenType.RPAREN)
        return Write(expr=expr, line=line)

    # =========================================================================
    # <lista_inst> → <instrucao> <resto_inst>
    # =========================================================================

    def lista_inst(self) -> List[Any]:
        stmt = self.instrucao()
        rest = self.resto_inst()
        return [stmt] + rest

    # =========================================================================
    # Expressões — precedência por níveis, sem recursão à esquerda
    # =========================================================================

    # <exp> → <exp_rel>
    def exp(self) -> Any:
        return self.exp_rel()

    # <exp_rel>  → <exp_ad> <exp_rel_linha>
    # <exp_rel_linha> → <relop> <exp_ad> <exp_rel_linha> | ε
    def exp_rel(self) -> Any:
        left = self.exp_ad()
        return self.exp_rel_linha(left)

    def exp_rel_linha(self, left: Any) -> Any:
        _RELOPS = {
            TokenType.IGUAL, TokenType.DIFERENTE,
            TokenType.MENOR, TokenType.MAIOR,
            TokenType.MENOR_IGUAL, TokenType.MAIOR_IGUAL,
        }
        if self.tok.type in _RELOPS:
            op    = self.relop()
            right = self.exp_ad()
            return self.exp_rel_linha(BinOp(op=op, left=left, right=right))
        return left     # ε

    # <exp_ad>  → <exp_mul> <exp_ad_linha>
    # <exp_ad_linha> → <addop> <exp_mul> <exp_ad_linha> | ε
    def exp_ad(self) -> Any:
        left = self.exp_mul()
        return self.exp_ad_linha(left)

    def exp_ad_linha(self, left: Any) -> Any:
        _ADDOPS = {TokenType.MAIS, TokenType.MENOS, TokenType.OR}
        if self.tok.type in _ADDOPS:
            op    = self.addop()
            right = self.exp_mul()
            return self.exp_ad_linha(BinOp(op=op, left=left, right=right))
        return left     # ε

    # <exp_mul>  → <exp_un> <exp_mul_linha>
    # <exp_mul_linha> → <mulop> <exp_un> <exp_mul_linha> | ε
    def exp_mul(self) -> Any:
        left = self.exp_un()
        return self.exp_mul_linha(left)

    def exp_mul_linha(self, left: Any) -> Any:
        _MULOPS = {
            TokenType.MULT, TokenType.DIV,
            TokenType.DIV_INT, TokenType.MOD, TokenType.AND,
        }
        if self.tok.type in _MULOPS:
            op    = self.mulop()
            right = self.exp_un()
            return self.exp_mul_linha(BinOp(op=op, left=left, right=right))
        return left     # ε

    # <exp_un> → not <exp_un> | + <exp_un> | - <exp_un> | <primario>
    def exp_un(self) -> Any:
        tt = self.tok.type

        if tt == TokenType.NOT:
            tok = self.casar(TokenType.NOT)
            return UnaryOp(op='not', operand=self.exp_un(), line=tok.line)

        elif tt == TokenType.MAIS:
            tok = self.casar(TokenType.MAIS)
            return UnaryOp(op='+', operand=self.exp_un(), line=tok.line)

        elif tt == TokenType.MENOS:
            tok = self.casar(TokenType.MENOS)
            return UnaryOp(op='-', operand=self.exp_un(), line=tok.line)

        elif tt in (TokenType.LPAREN, TokenType.ID,
                    TokenType.CONST_INT, TokenType.CONST_REAL,
                    TokenType.CONST_STRING, TokenType.CONST_BOOL):
            return self.primario()

        else:
            self.erroSintatico("expressão esperada")

    # <primario> → ( <exp> ) | id | <const>
    def primario(self) -> Any:
        tt = self.tok.type

        if tt == TokenType.LPAREN:
            self.casar(TokenType.LPAREN)
            expr = self.exp()
            self.casar(TokenType.RPAREN)
            return expr

        elif tt == TokenType.ID:
            tok = self.casar(TokenType.ID)
            return Var(name=tok.lexeme, line=tok.line)

        else:
            return self.const()

    # =========================================================================
    # Terminais de operadores e constantes
    # =========================================================================

    # <relop> → == | <> | < | > | <= | >=
    def relop(self) -> str:
        tt = self.tok.type
        if tt == TokenType.IGUAL:
            self.casar(TokenType.IGUAL);        return '=='
        elif tt == TokenType.DIFERENTE:
            self.casar(TokenType.DIFERENTE);    return '<>'
        elif tt == TokenType.MENOR:
            self.casar(TokenType.MENOR);        return '<'
        elif tt == TokenType.MAIOR:
            self.casar(TokenType.MAIOR);        return '>'
        elif tt == TokenType.MENOR_IGUAL:
            self.casar(TokenType.MENOR_IGUAL);  return '<='
        elif tt == TokenType.MAIOR_IGUAL:
            self.casar(TokenType.MAIOR_IGUAL);  return '>='
        else:
            self.erroSintatico("operador relacional esperado")

    # <addop> → + | - | ou
    def addop(self) -> str:
        tt = self.tok.type
        if tt == TokenType.MAIS:
            self.casar(TokenType.MAIS);   return '+'
        elif tt == TokenType.MENOS:
            self.casar(TokenType.MENOS);  return '-'
        elif tt == TokenType.OR:
            self.casar(TokenType.OR);     return 'ou'
        else:
            self.erroSintatico("operador aditivo esperado")

    # <mulop> → * | / | div | mod | &&
    def mulop(self) -> str:
        tt = self.tok.type
        if tt == TokenType.MULT:
            self.casar(TokenType.MULT);     return '*'
        elif tt == TokenType.DIV:
            self.casar(TokenType.DIV);      return '/'
        elif tt == TokenType.DIV_INT:
            self.casar(TokenType.DIV_INT);  return 'div'
        elif tt == TokenType.MOD:
            self.casar(TokenType.MOD);      return 'mod'
        elif tt == TokenType.AND:
            self.casar(TokenType.AND);      return '&&'
        else:
            self.erroSintatico("operador multiplicativo esperado")

    # <const> → num_int | num_real | cadeia | verdadeiro | falso
    def const(self) -> Any:
        tt  = self.tok.type
        tok = self.tok
        if tt == TokenType.CONST_INT:
            self.casar(TokenType.CONST_INT)
            return IntConst(value=int(tok.lexeme))
        elif tt == TokenType.CONST_REAL:
            self.casar(TokenType.CONST_REAL)
            return RealConst(value=float(tok.lexeme))
        elif tt == TokenType.CONST_STRING:
            self.casar(TokenType.CONST_STRING)
            return StringConst(value=tok.lexeme[1:-1])   # remove aspas
        elif tt == TokenType.CONST_BOOL:
            self.casar(TokenType.CONST_BOOL)
            return BoolConst(value=(tok.lexeme == 'verdadeiro'))
        else:
            self.erroSintatico("constante esperada")


# =============================================================================
# Ponto de entrada público
# =============================================================================

def parse_tokens(tokens: List[Token]) -> Program:
    """Recebe lista de tokens do léxico e devolve a AST."""
    return Parser(tokens).parse()
