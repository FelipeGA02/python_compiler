from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Any


def print_ast(node, indent: int = 0) -> None:
    prefix = "  " * indent
    if isinstance(node, list):
        for item in node:
            print_ast(item, indent)
        return
    if isinstance(node, Program):
        print(f"{prefix}Programa '{node.name}'")
        for d in node.decls:
            print_ast(d, indent + 1)
        for s in node.stmts:
            print_ast(s, indent + 1)
    elif isinstance(node, VarDecl):
        print(f"{prefix}Decl {', '.join(node.names)} : {node.type}")
    elif isinstance(node, Assign):
        print(f"{prefix}Atrib {node.name} :=")
        print_ast(node.expr, indent + 2)
    elif isinstance(node, If):
        print(f"{prefix}Se")
        print_ast(node.cond, indent + 2)
        print(f"{prefix}  Entao")
        for s in node.then_stmts:
            print_ast(s, indent + 2)
        if node.else_stmts:
            print(f"{prefix}  Senao")
            for s in node.else_stmts:
                print_ast(s, indent + 2)
    elif isinstance(node, While):
        print(f"{prefix}Enquanto")
        print_ast(node.cond, indent + 2)
        print(f"{prefix}  Faca")
        for s in node.body:
            print_ast(s, indent + 2)
    elif isinstance(node, Read):
        print(f"{prefix}Leia({', '.join(node.names)})")
    elif isinstance(node, Write):
        print(f"{prefix}Escreva")
        print_ast(node.expr, indent + 2)
    elif isinstance(node, BinOp):
        print(f"{prefix}BinOp '{node.op}'")
        print_ast(node.left, indent + 2)
        print_ast(node.right, indent + 2)
    elif isinstance(node, UnaryOp):
        print(f"{prefix}UnOp '{node.op}'")
        print_ast(node.operand, indent + 2)
    elif isinstance(node, Var):
        print(f"{prefix}Var '{node.name}'")
    elif isinstance(node, IntConst):
        print(f"{prefix}Int {node.value}")
    elif isinstance(node, RealConst):
        print(f"{prefix}Real {node.value}")
    elif isinstance(node, StringConst):
        print(f"{prefix}Str '{node.value}'")
    elif isinstance(node, BoolConst):
        print(f"{prefix}Bool {'verdadeiro' if node.value else 'falso'}")
    else:
        print(f"{prefix}{node!r}")


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
