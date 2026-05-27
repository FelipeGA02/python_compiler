"""
Analisador Semântico para a linguagem BRL.

Verifica, em uma única passagem sobre a AST:
  1. Declaração antes do uso de variáveis.
  2. Ausência de re-declaração dentro do mesmo escopo.
  3. Compatibilidade de tipos em atribuições.
  4. Condições de 'se'/'enquanto' devem ser do tipo 'logico'.
  5. Inferência de tipos em expressões com promoção inteiro→real.
"""
from __future__ import annotations
from typing import Dict, Optional, Any

from src.parser.ast_nodes import (
    Program, VarDecl, Assign, If, While, Read, Write,
    BinOp, UnaryOp, Var, IntConst, RealConst, StringConst, BoolConst,
)
from src.utils.error import SemanticError


# Tipos válidos da linguagem
_NUMERIC = frozenset({'inteiro', 'real'})
_ALL_TYPES = frozenset({'inteiro', 'real', 'logico', 'caractere'})


class SemanticAnalyzer:
    def __init__(self):
        # Mapa nome → tipo declarado
        self._symbols: Dict[str, str] = {}

    # ── Ponto de entrada ──────────────────────────────────────────────────────

    def analyze(self, program: Program) -> None:
        for decl in program.decls:
            self._visit_decl(decl)
        for stmt in program.stmts:
            self._visit_stmt(stmt)

    # ── Declarações ───────────────────────────────────────────────────────────

    def _visit_decl(self, decl: VarDecl) -> None:
        for name in decl.names:
            if name in self._symbols:
                raise SemanticError(f"variável '{name}' já foi declarada")
            if decl.type not in _ALL_TYPES:
                raise SemanticError(f"tipo desconhecido '{decl.type}'")
            self._symbols[name] = decl.type

    # ── Instruções ────────────────────────────────────────────────────────────

    def _visit_stmt(self, stmt: Any) -> None:
        if isinstance(stmt, Assign):
            self._visit_assign(stmt)
        elif isinstance(stmt, If):
            self._visit_if(stmt)
        elif isinstance(stmt, While):
            self._visit_while(stmt)
        elif isinstance(stmt, Read):
            self._visit_read(stmt)
        elif isinstance(stmt, Write):
            self._visit_write(stmt)
        else:
            raise SemanticError(f"instrução desconhecida: {type(stmt).__name__}")

    def _visit_assign(self, stmt: Assign) -> None:
        if stmt.name not in self._symbols:
            raise SemanticError(
                f"variável '{stmt.name}' não declarada", stmt.line
            )
        var_type = self._symbols[stmt.name]
        expr_type = self._infer(stmt.expr)
        self._check_assign_compat(var_type, expr_type, stmt.name, stmt.line)

    def _visit_if(self, stmt: If) -> None:
        cond_type = self._infer(stmt.cond)
        if cond_type != 'logico':
            raise SemanticError(
                f"condição de 'se' deve ser do tipo 'logico', encontrado '{cond_type}'",
                stmt.line,
            )
        for s in stmt.then_stmts:
            self._visit_stmt(s)
        if stmt.else_stmts:
            for s in stmt.else_stmts:
                self._visit_stmt(s)

    def _visit_while(self, stmt: While) -> None:
        cond_type = self._infer(stmt.cond)
        if cond_type != 'logico':
            raise SemanticError(
                f"condição de 'enquanto' deve ser do tipo 'logico', encontrado '{cond_type}'",
                stmt.line,
            )
        for s in stmt.body:
            self._visit_stmt(s)

    def _visit_read(self, stmt: Read) -> None:
        for name in stmt.names:
            if name not in self._symbols:
                raise SemanticError(
                    f"variável '{name}' não declarada em 'leia'", stmt.line
                )

    def _visit_write(self, stmt: Write) -> None:
        self._infer(stmt.expr)   # valida a expressão, resultado descartado

    # ── Inferência de tipos ───────────────────────────────────────────────────

    def _infer(self, expr: Any) -> str:
        if isinstance(expr, IntConst):
            expr.inferred_type = 'inteiro'
            return 'inteiro'

        if isinstance(expr, RealConst):
            expr.inferred_type = 'real'
            return 'real'

        if isinstance(expr, StringConst):
            expr.inferred_type = 'caractere'
            return 'caractere'

        if isinstance(expr, BoolConst):
            expr.inferred_type = 'logico'
            return 'logico'

        if isinstance(expr, Var):
            if expr.name not in self._symbols:
                raise SemanticError(
                    f"variável '{expr.name}' não declarada", expr.line
                )
            t = self._symbols[expr.name]
            expr.inferred_type = t
            return t

        if isinstance(expr, UnaryOp):
            return self._infer_unary(expr)

        if isinstance(expr, BinOp):
            return self._infer_binary(expr)

        raise SemanticError(f"nó de expressão desconhecido: {type(expr).__name__}")

    # ── Operadores unários ────────────────────────────────────────────────────

    def _infer_unary(self, expr: UnaryOp) -> str:
        op_type = self._infer(expr.operand)

        if expr.op == 'not':
            if op_type != 'logico':
                raise SemanticError(
                    f"operador 'not' requer operando 'logico', encontrado '{op_type}'",
                    expr.line,
                )
            expr.inferred_type = 'logico'
            return 'logico'

        if expr.op in ('+', '-'):
            if op_type not in _NUMERIC:
                raise SemanticError(
                    f"operador unário '{expr.op}' requer tipo numérico, encontrado '{op_type}'",
                    expr.line,
                )
            expr.inferred_type = op_type
            return op_type

        raise SemanticError(f"operador unário desconhecido '{expr.op}'", expr.line)

    # ── Operadores binários ───────────────────────────────────────────────────

    def _infer_binary(self, expr: BinOp) -> str:
        lt = self._infer(expr.left)
        rt = self._infer(expr.right)
        op = expr.op
        result = self._binary_result_type(op, lt, rt, expr.line)
        expr.inferred_type = result
        return result

    def _binary_result_type(self, op: str, lt: str, rt: str, line: int) -> str:

        # ── Relacionais → sempre produzem logico ─────────────────────────────
        if op in ('==', '<>'):
            if lt == rt:
                return 'logico'
            if lt in _NUMERIC and rt in _NUMERIC:
                return 'logico'
            raise SemanticError(
                f"operador '{op}' não pode comparar '{lt}' com '{rt}'", line
            )

        if op in ('<', '>', '<=', '>='):
            if (lt in _NUMERIC and rt in _NUMERIC) or (lt == rt == 'caractere'):
                return 'logico'
            raise SemanticError(
                f"operador '{op}' não pode comparar '{lt}' com '{rt}'", line
            )

        # ── Lógicos binários (&&, ou) ─────────────────────────────────────────
        if op in ('&&', 'ou'):
            if lt != 'logico' or rt != 'logico':
                raise SemanticError(
                    f"operador '{op}' requer dois operandos 'logico', "
                    f"encontrado '{lt}' e '{rt}'", line
                )
            return 'logico'

        # ── Aditivos (+ ─) ────────────────────────────────────────────────────
        if op == '+':
            if lt == 'caractere' and rt == 'caractere':
                return 'caractere'   # concatenação de strings
            return self._numeric_result(op, lt, rt, line)

        if op == '-':
            return self._numeric_result(op, lt, rt, line)

        # ── Multiplicativos (* /) ─────────────────────────────────────────────
        if op in ('*', '/'):
            return self._numeric_result(op, lt, rt, line)

        # ── Divisão inteira e módulo ──────────────────────────────────────────
        if op in ('div', 'mod'):
            if lt != 'inteiro' or rt != 'inteiro':
                raise SemanticError(
                    f"operador '{op}' requer dois operandos 'inteiro', "
                    f"encontrado '{lt}' e '{rt}'", line
                )
            return 'inteiro'

        raise SemanticError(f"operador binário desconhecido '{op}'", line)

    def _numeric_result(self, op: str, lt: str, rt: str, line: int) -> str:
        if lt not in _NUMERIC or rt not in _NUMERIC:
            raise SemanticError(
                f"operador '{op}' requer operandos numéricos, "
                f"encontrado '{lt}' e '{rt}'", line
            )
        return 'real' if ('real' in (lt, rt)) else 'inteiro'

    # ── Compatibilidade de atribuição ─────────────────────────────────────────

    def _check_assign_compat(
        self, var_type: str, expr_type: str, name: str, line: int
    ) -> None:
        if var_type == expr_type:
            return
        # Promoção implícita inteiro → real
        if var_type == 'real' and expr_type == 'inteiro':
            return
        raise SemanticError(
            f"tipo incompatível na atribuição de '{name}': "
            f"variável é '{var_type}', expressão é '{expr_type}'",
            line,
        )

    # ── Acesso à tabela de símbolos resultado ─────────────────────────────────

    @property
    def symbols(self) -> Dict[str, str]:
        return dict(self._symbols)


def analyze(program: Program) -> Dict[str, str]:
    """Ponto de entrada conveniente: analisa o programa e devolve o mapa nome→tipo."""
    sa = SemanticAnalyzer()
    sa.analyze(program)
    return sa.symbols
