from typing import List
from scanner import Token, TokenType
from expr import *


class LoxParserException(Exception):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> List[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.decl())
        return statements
    
    def decl(self):
        try:
            if self.match(TokenType.VAR):
                return self.vardecl()
            return self.statement()
        except LoxParserException as e:
            print(e)
            self.sync()
    
    def vardecl(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name")

        init = None
        if self.match(TokenType.EQUAL):
            init = self.expression()
        
        self.consume(TokenType.SEMICOLON, 'Expect ; after variable decl')
        return VarStmt(name, init)
    
    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return self.block()
        if self.match(TokenType.IF):
            return self.ifstmt()
        if self.match(TokenType.WHILE):
            return self.whilestmt()
        if self.match(TokenType.FOR):
            return self.forstmt()
        return self.expression_statement()
    
    def whilestmt(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "while"')
        cond = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after "while"')
        body = self.statement()
        return WhileStmt(cond, body)

    def forstmt(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "for"')
        
        init = None
        if self.match(TokenType.SEMICOLON):
            init = None
        elif self.match(TokenType.VAR):
            init = self.vardecl()
        else:
            init = self.expression_statement()
        
        cond = None
        if not self.check(TokenType.SEMICOLON):
            cond = self.expression()
        self.consume(TokenType.SEMICOLON, 'Expect ";" after loop condition')

        incr = None
        if not self.check(TokenType.RIGHT_PAREN):
            incr = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after loop clauses')

        body = self.statement()

        if incr is not None:
            body = Block([body, ExpressionStmt(incr)])
        
        if cond is None:
            cond = Literal(True)
        body = WhileStmt(cond, body)

        if init is not None:
            body = Block([init, body])
        
        return body

    def ifstmt(self):
        self.consume(TokenType.LEFT_PAREN, 'Expect "(" after "if"')
        cond = self.expression()
        self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after "if"')

        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfStmt(cond, then_branch, else_branch)
    
    def print_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; in print")
        return PrintStmt(expr)
    
    def block(self):
        stmts = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmts.append(self.decl())
        self.consume(TokenType.RIGHT_BRACE, 'Expect } after block')
        return Block(stmts)

    
    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ; after expression")
        return ExpressionStmt(expr)


    def expression(self) -> Expr:
        return self.assignment()
    
    def assignment(self) -> Expr:
        expr = self.or_stmt()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            val = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, val)
            raise LoxParserException("Invalid assignment target")
        return expr
    
    def or_stmt(self) -> Expr:
        expr = self.and_stmt()
        while self.match(TokenType.OR):
            op = self.previous()
            right = self.and_stmt()
            expr = Logical(expr, op, right)
        return expr

    def and_stmt(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            op = self.previous()
            right = self.equality()
            expr = Logical(expr, op, right)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:
        expr = self.addition()

        while self.match(
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
                TokenType.LESS,
                TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)

        return expr

    def addition(self) -> Expr:
        expr = self.multiplication()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.multiplication()
            expr = Binary(expr, operator, right)

        return expr

    def multiplication(self) -> Expr:
        expr = self.unary()

        while self.match(TokenType.STAR, TokenType.SLASH):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()
    
    def call(self) -> Expr:
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishcall(expr)
            else:
                break
        return expr
    
    def finishcall(self, callee) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            while (self.match(TokenType.COMMA)):
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, 'Expect ")" after args')
        return Call(callee, paren, arguments)


    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')'")
            return Grouping(expr)

        print("Expect expr")

    def match(self, *args) -> bool:
        for ttype in args:
            if self.check(ttype):
                self.advance()
                return True
        return False

    def consume(self, ttype: TokenType, msg) -> Token:
        if self.check(ttype):
            return self.advance()

        raise LoxParserException(msg)

    def check(self, ttype: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().ttype == ttype

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        return self.peek().ttype == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def sync(self):
        self.advance()

        while not self.is_at_end():
            if self.previous() == TokenType.SEMICOLON:
                break
            if self.peek().ttype in [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]:
                break
            self.advance()
