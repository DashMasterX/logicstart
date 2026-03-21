# engine.py
from parser import Parser
from executor import Executor
from errors import LogicStartErro

class LogicStart:
    """
    Motor principal da linguagem LogicStart (português)
    """
    def __init__(self, codigo):
        self.codigo = codigo
        self.parser = Parser(codigo)
        self.executor = Executor()
        self.ast = None

    def compilar(self):
        try:
            self.ast = self.parser.parse()
        except LogicStartErro as e:
            raise LogicStartErro(f"Erro de compilação: {e}")
        except Exception as e:
            raise LogicStartErro(f"Erro inesperado na compilação: {e}")

    def executar(self):
        if not self.ast:
            self.compilar()
        try:
            self.executor.executar(self.ast)
        except LogicStartErro as e:
            raise LogicStartErro(f"Erro de execução: {e}")
        except Exception as e:
            raise LogicStartErro(f"Erro inesperado na execução: {e}")

    def resultado(self):
        """
        Retorna tudo que foi impresso pelo código
        """
        return "\n".join(self.executor.output)
