# engine.py
import re
from errors import LogicStartErro
from executor import Executor

class LogicStart:
    """
    Engine profissional LogicStart.
    Interpreta JavaScript em português, comandos traduzidos.
    """
    # Palavras-chave traduzidas
    PALAVRAS_CHAVE = {
        'se': 'if',
        'senao': 'else',
        'enquanto': 'while',
        'para': 'for',
        'funcao': 'function',
        'retorne': 'return',
        'imprima': 'console.log',
        'constante': 'const',
        'variavel': 'let',
        'classe': 'class',
        'novo': 'new'
    }

    def __init__(self, codigo: str):
        self.codigo_original = codigo
        self.codigo_traduzido = ""
        self.executor = Executor()

    def traduzir(self):
        """
        Traduz a sintaxe LogicStart (português) para JS padrão.
        """
        codigo = self.codigo_original

        # Substitui palavras-chave traduzidas
        for pt, js in self.PALAVRAS_CHAVE.items():
            # Usa regex para não substituir dentro de strings
            codigo = re.sub(rf'\b{pt}\b', js, codigo)

        self.codigo_traduzido = codigo

    def executar(self):
        """
        Executa o código traduzido usando Executor seguro.
        """
        self.traduzir()
        try:
            self.executor.executar(self.codigo_traduzido)
        except Exception as e:
            raise LogicStartErro(f"Erro na execução: {e}")

    def autocomplete(self, prefixo: str):
        """
        Retorna lista de sugestões para autocompletar.
        """
        sugestoes = [k for k in self.PALAVRAS_CHAVE.keys() if k.startswith(prefixo)]
        return sugestoes
