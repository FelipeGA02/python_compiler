from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any


# ── Statements ────────────────────────────────────────────────────────────────

@dataclass
class Program:
    name: str
    decls: List[VarDecl]
    stmts: List[Any]   # list of statement nodes


@dataclass
class VarDecl:
    names: List[str]
    type: str          # 'inteiro' | 'real' | 'logico' | 'caractere'


@dataclass
class Assign:
    name: str
    expr: Any          # expression node
    line: int = 0


@dataclass
class If:
    cond: Any
    then_stmts: List[Any]
    else_stmts: Optional[List[Any]]
    line: int = 0


@dataclass
class While:
    cond: Any
    body: List[Any]
    line: int = 0


@dataclass
class Read:
    names: List[str]
    line: int = 0


@dataclass
class Write:
    expr: Any
    line: int = 0


# ── Expressions ───────────────────────────────────────────────────────────────

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any
    inferred_type: Optional[str] = field(default=None, repr=False)
    line: int = 0


@dataclass
class UnaryOp:
    op: str
    operand: Any
    inferred_type: Optional[str] = field(default=None, repr=False)
    line: int = 0


@dataclass
class Var:
    name: str
    inferred_type: Optional[str] = field(default=None, repr=False)
    line: int = 0


@dataclass
class IntConst:
    value: int
    inferred_type: str = field(default='inteiro', repr=False)


@dataclass
class RealConst:
    value: float
    inferred_type: str = field(default='real', repr=False)


@dataclass
class StringConst:
    value: str
    inferred_type: str = field(default='caractere', repr=False)


@dataclass
class BoolConst:
    value: bool
    inferred_type: str = field(default='logico', repr=False)
