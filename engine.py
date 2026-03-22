import re
import ast

class EnginePythonPortugues:
    """
    Engine Python em português – completa, segura e multiplataforma.
    """

    # Tradução do português -> Python
    TRADUCOES = {
        "variavel": "",       # variavel x = 10 -> x = 10
        "imprimir": "print",
        "se": "if",
        "senao": "else",
        "enquanto": "while",
        "para": "for",
        "funcao": "def",
        "retorna": "return",
        "entrada": "input"
    }

    # Comandos/recursos bloqueados por segurança
    BLOQUEIOS = ["os.", "open(", "exec(", "__import__", "eval(", "compile("]

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.saida = []      # Captura de outputs
        self.variaveis = {}  # Armazena variáveis globais
        self.funcoes = {}    # Armazena funções definidas
        self.historico = []  # Armazena histórico de código executado

    def traduzir_linha(self, linha: str) -> str:
        linha = linha.strip()
        for pt, py in self.TRADUCOES.items():
            if pt in linha:
                if pt == "variavel":
                    linha = linha.replace("variavel", "", 1).strip()
                else:
                    linha = linha.replace(pt, py)
        return linha

    def verificar_segurança(self, linha: str):
        for bloqueio in self.BLOQUEIOS:
            if bloqueio in linha:
                raise Exception(f"Acesso bloqueado na linha: {linha}")

    def executar(self):
        linhas = self.codigo.splitlines()
        codigo_traduzido = ""

        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith("//"):  # Ignora comentários
                continue

            self.verificar_segurança(linha)
            codigo_traduzido += self.traduzir_linha(linha) + "\n"

        # Ambiente seguro para execução
        exec_env = {}
        try:
            exec(
                codigo_traduzido,
                {"__builtins__": {
                    "print": self._print,
                    "input": input,
                    "range": range,
                    "len": len,
                    "int": int,
                    "float": float,
                    "str": str,
                    "list": list,
                    "dict": dict,
                    "sum": sum,
                    "max": max,
                    "min": min,
                }},
                exec_env
            )
            self.historico.append(self.codigo)
        except Exception as e:
            raise Exception(f"Erro na execução: {e}")

    def _print(self, *args, **kwargs):
        texto = " ".join(str(a) for a in args)
        self.saida.append(texto)
        print(texto)

# ------------------------------
# EXEMPLO DE USO
# ------------------------------
codigo = """
// Exemplo completo de Python em português
variavel x = 10
variavel y = 5

se x > y:
    imprimir("X é maior que Y")
senao:
    imprimir("X não é maior que Y")

enquanto y < x:
    imprimir(y)
    y = y + 1

para i em range(3):
    imprimir(i)

funcao soma(a, b):
    imprimir(a + b)
    
soma(10, 20)

variavel nome = entrada("Qual é o seu nome? ")
imprimir("Olá", nome)
"""

engine = EnginePythonPortugues(codigo)
engine.executar()

# Saída capturada
print("\n--- Saída Capturada ---")
for linha in engine.saida:
    print(linha)

# Histórico
print("\n--- Histórico ---")
for item in engine.historico:
    print(item)
