from parser import parse
from executor import Executor
from errors import LogicStartErro

class LogicStart:
    def __init__(self, codigo):
        self.linhas = codigo.strip().split("\n")

    def executar(self):
        try:
            ast = parse(self.linhas)
            executor = Executor()
            executor.executar(ast)
        except LogicStartErro as e:
            print(f"❌ Erro: {e}")