# from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    # One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()


class Token:
    def __init__(self, ttype, lexeme, literal, line):
        self.ttype = ttype
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    def __repr__(self):
        return f"<{self.ttype}:{self.line}: {self.lexeme}>"


keywords = {
    "and":   TokenType.AND,
    "class": TokenType.CLASS,
    "else":  TokenType.ELSE,
    "false": TokenType.FALSE,
    "for":   TokenType.FOR,
    "fun":   TokenType.FUN,
    "if":    TokenType.IF,
    "nil":   TokenType.NIL,
    "or":    TokenType.OR,
    "print": TokenType.PRINT,
    "return":TokenType.RETURN,
    "super": TokenType.SUPER,
    "this":  TokenType.THIS,
    "true":  TokenType.TRUE,
    "var":   TokenType.VAR,
    "while": TokenType.WHILE,
}


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match(
                '=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match(
                '=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match(
                '=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match(
                '=') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                self.block_comment()
            else:
                self.add_token(TokenType.SLASH)
        elif c in [' ', '\r', '\t']:
            return None  # Ignore Whitespace
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        else:
            if c.isdigit():
                self.number()
            elif c.isalpha():
                self.identifier()
            else:
                print("Unexpected Character")

    def identifier(self):
        while self.peek().isalnum():
            self.advance()
        text = self.source[self.start: self.current]
        ttype = keywords.get(text)
        if ttype == None:
            ttype = TokenType.IDENTIFIER
        self.add_token(ttype)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # Consume the '.'

            while self.peek().isdigit():
                self.advance()

        self.add_token(TokenType.NUMBER, float(
            self.source[self.start: self.current]))

    def string(self):
        while (self.peek() != '"') and (not self.is_at_end()):
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            print(f"{self.line}: Unterminated string.")
            return None

        self.advance()  # The closing '"'
        value = self.source[self.start + 1: self.current - 1]
        self.add_token(TokenType.STRING, value)

    def block_comment(self):
        while not self.is_at_end():
            c = self.advance()
            if c == '/' and self.match('*'):
                self.block_comment()
            elif c == '*' and self.match('/'):
                return None
            elif c == '\n':
                self.line += 1

    def match(self, expected) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self) -> str:
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, ttype: TokenType, literal=None):
        text = self.source[self.start: self.current]
        self.tokens.append(Token(ttype, text, literal, self.line))
