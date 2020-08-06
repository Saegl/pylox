from dataclasses import dataclass
from typing import List
from scanner import Token


class Expr:
    pass


@dataclass
class Assign(Expr):
    name: Token
    val: Expr

    def __repr__(self):
        return f"({self.name} = {self.val})"


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __repr__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"


@dataclass
class Call(Expr):
    calle: Expr
    paren: Token
    arguments: List[Expr]

    def __repr__(self):
        return f"{self.paren}({self.arguments})"


@dataclass
class Grouping(Expr):
    expression: Expr

    def __repr__(self):
        return f"({self.expression})"


@dataclass
class Literal(Expr):
    value: object

    def __repr__(self):
        return f"{self.value}"


@dataclass
class Logical(Expr):
    left: Expr
    op: Token
    right: Expr

    def __repr__(self):
        return f"({self.left} {self.op.lexeme} {self.right})"


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def __repr__(self):
        return f"<{self.operator.lexeme} {self.right}>"


@dataclass
class Variable(Expr):
    name: Token

    def __repr__(self):
        return f"<{self.name.lexeme}>"


class Stmt:
    pass


@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def __repr__(self):
        return f"<<{self.statements}>>"


@dataclass
class ExpressionStmt(Stmt):
    expression: Expr

    def __repr__(self):
        return f"<<{self.expression}>>"


@dataclass
class PrintStmt(Stmt):
    expression: Expr

    def __repr__(self):
        return f"<<PRINT {self.expression}>>"


@dataclass
class WhileStmt(Stmt):
    cond: Expr
    body: Stmt


@dataclass
class VarStmt(Stmt):
    name: Token
    initalizer: Expr

    def __repr__(self):
        return f"<<{str(self.name)} := {self.initalizer}>>"


@dataclass
class IfStmt(Stmt):
    cond: Expr
    then_branch: Stmt
    else_branch: Stmt


if __name__ == "__main__":
    print(Binary(Literal(1), '+', Literal(2)))
