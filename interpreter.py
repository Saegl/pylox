import time
from expr import *
from scanner import TokenType
from abc import ABC


class LoxRuntimeError(Exception):
    pass


class LoxCallabe(ABC):
    def arity(self) -> int:
        pass

    def call(self, interpreter, arguments: List):
        pass


class Environment:
    def __init__(self, env):
        self.previous = env
        self.values = {}

    def define(self, name, val):
        self.values[name] = val

    def assign(self, name, val):
        if self.values.get(name) is not None:
            self.values[name] = val
            return None
        if self.previous is not None:
            self.previous.assign(name, val)
            return None
        raise LoxRuntimeError(
            f'undefined variable {name}, cannot assign {val}')

    def get(self, name):
        val = self.values.get(name)
        if val is not None:
            return val

        if self.previous is not None:
            val = self.previous.get(name)
            if val is not None:
                return val

        raise LoxRuntimeError(f"Varname {name} is never assigned")


class Interpreter:
    def __init__(self):
        self.globalenv = Environment(None)
        self.env = self.globalenv

        class Clock(LoxCallabe):
            def arity(self):
                return 0

            def call(self):
                return time.time()
        
        self.globalenv.define("clock", Clock())

    def interpret(self, stmts: List[Stmt]):
        try:
            for stmt in stmts:
                self.eval(stmt)
        except LoxRuntimeError as e:
            print(e)

    def eval(self, expr):
        attr = expr.__class__.__name__.lower()
        return getattr(self, attr)(expr)

    def binary(self, expr: Binary):
        left = self.eval(expr.left)
        right = self.eval(expr.right)
        op = expr.operator.ttype

        if op == TokenType.BANG_EQUAL:
            return not self.is_equal(left, right)
        if op == TokenType.EQUAL_EQUAL:
            return self.is_equal(left, right)
        if op == TokenType.GREATER:
            self.check_number(left, right)
            return left > right
        if op == TokenType.GREATER_EQUAL:
            self.check_number(left, right)
            return left >= right
        if op == TokenType.LESS:
            self.check_number(left, right)
            return left < right
        if op == TokenType.LESS_EQUAL:
            self.check_number(left, right)
            return left <= right
        if op == TokenType.MINUS:
            self.check_number(left, right)
            return left - right
        if op == TokenType.PLUS:
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            if isinstance(left, float) and isinstance(right, float):
                return left + right

            raise LoxRuntimeError("Wrong types for addition")
        if op == TokenType.SLASH:
            self.check_number(left, right)
            if (right == 0.0):
                raise LoxRuntimeError("Cannot divide by zero")
            return left / right
        if op == TokenType.STAR:
            self.check_number(left, right)
            return left * right

    def group(self, expr: Grouping):
        return self.eval(expr)

    def literal(self, expr: Literal):
        return expr.value

    def unary(self, expr: Unary):
        right = self.eval(expr.right)

        op = expr.operator.ttype
        if op == TokenType.BANG:
            return not self.is_truthy(right)
        if op == TokenType.MINUS:
            self.check_number(right)
            return -right
        else:
            raise LoxRuntimeError("Unreachable")

    def check_number(self, *args):
        res = all(map(lambda x: isinstance(x, float), args))
        if not res:
            raise LoxRuntimeError("Operands must be numbers")

    def is_truthy(self, x):
        if x is None:
            return False
        if isinstance(x, bool):
            return x
        return True

    def is_equal(self, a, b):
        return a == b

    def expressionstmt(self, stmt: ExpressionStmt):
        self.eval(stmt.expression)
        return None

    def printstmt(self, stmt: PrintStmt):
        val = self.eval(stmt.expression)
        print(val)
        return None

    def varstmt(self, stmt: VarStmt):
        val = None
        if stmt.initalizer != None:
            val = self.eval(stmt.initalizer)

        self.env.define(stmt.name.lexeme, val)

        return None

    def variable(self, stmt: Variable):
        val = self.env.get(stmt.name.lexeme)
        if val is None:
            raise LoxRuntimeError('Variable is never assigned')
        return val

    def assign(self, stmt: Assign):
        val = self.eval(stmt.val)
        self.env.assign(stmt.name.lexeme, val)
        return val

    def block(self, stmt: Block):
        prev = self.env
        try:
            self.env = Environment(prev)
            for stmt in stmt.statements:
                self.eval(stmt)
        finally:
            self.env = prev

    def ifstmt(self, stmt: IfStmt):
        if self.is_truthy(self.eval(stmt.cond)):
            self.eval(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.eval(stmt.else_branch)

    def whilestmt(self, stmt: WhileStmt):
        while (self.is_truthy(self.eval(stmt.cond))):
            self.eval(stmt.body)

    def logical(self, stmt: Logical):
        left = self.eval(stmt.left)

        if stmt.op.ttype == TokenType.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.eval(stmt.right)

    def call(self, expr: Call):
        callee = self.eval(expr.calle)

        arguments = []
        for arg in expr.arguments:
            arguments.append(self.eval(arg))

        function = callee
        if len(arguments) != function.arity():
            raise LoxRuntimeError(
                f"Expected {function.arity()} arguments but got {arguments.size()}.")
        return function.call(*arguments)
