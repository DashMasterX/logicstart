# engine.py
from lexer import Lexer
from parser import Parser
from executor import Executor
from errors import LogicStartErro

class LogicStart:
    def __init__(self, codigo):
        self.codigo = codigo

    def executar(self):
        # Lexer
        tokens = Lexer(self.codigo).gerar_tokens()

        # Parser
        ast = Parser(tokens).parse()

        # Executor
        Executor(ast).executar()
