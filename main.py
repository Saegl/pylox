import argparse
import scanner
import loxparser
from interpreter import Interpreter

class Lox:
    def __init__(self, debug):
        self.had_error = False
        self.debug = debug
        self.interpreter = Interpreter()
    
    def run_file(self, s):
        with open(s) as f:
            self.run(f.read())
        if self.had_error:
            print("Error in lox interpreter")
    def run_prompt(self):
        while True:
            self.run(input('lox> '))
            self.had_error = False
    def run(self, s):
        scan = scanner.Scanner(s)
        tokens = scan.scan_tokens()

        if self.debug:
            print("Tokens debug: ")
            for tok in tokens:
                print(tok)
        
        parser = loxparser.Parser(tokens)
        stmts = parser.parse()
        
        if self.debug:
            print("AST debug: ")
            print(stmts)

        self.interpreter.interpret(stmts)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument('--debug', help='show tokens and AST', action='store_true')
    argparser.add_argument('script', nargs='?', type=str, default='repl')
    args = argparser.parse_args()

    lox = Lox(args.debug)

    if args.script == 'repl':
        lox.run_prompt()
    else:
        script_path = args.script
        lox.run_file(script_path)
