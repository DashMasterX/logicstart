# engine.py
from lexer import Lexer
from parser import Parser
from nodes import Program
from errors import LogicStartErro

class LogicStart:
    """
    Engine principal da linguagem LogicStart (versão profissional)
    Traduz e executa código em português inspirado no JavaScript
    """

    def __init__(self, codigo: str):
        if not codigo or not codigo.strip():
            raise LogicStartErro("Código vazio não pode ser executado")
        
        self.codigo = codigo
        self.lexer = Lexer(codigo)
        self.parser = Parser(self.lexer)
        self.programa = None
        self.output_buffer = []

    def executar(self):
        """
        Executa o código
        """
        try:
            # Cria AST
            self.programa = self.parser.parse()
            
            # Executa o programa
            self._executar_nodo(self.programa)
        except LogicStartErro as e:
            raise e
        except Exception as e:
            raise LogicStartErro(f"Erro interno: {e}")

    def _executar_nodo(self, nodo):
        """
        Executa qualquer nodo da AST
        """
        if nodo is None:
            return None

        metodo = f"_executar_{type(nodo).__name__}"
        if hasattr(self, metodo):
            return getattr(self, metodo)(nodo)
        else:
            # Nodo genérico
            for filho in getattr(nodo, "filhos", []):
                self._executar_nodo(filho)

    # =========================
    # Nodificação de saída
    # =========================
    def _executar_Program(self, nodo: Program):
        for stmt in nodo.filhos:
            self._executar_nodo(stmt)

    def imprimir(self, valor):
        """
        Função para saída padrão (console)
        """
        self.output_buffer.append(str(valor))

    def get_output(self):
        """
        Retorna o resultado da execução
        """
        return "\n".join(self.output_buffer)
