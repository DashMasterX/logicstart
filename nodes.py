# nodes.py - Nodes completos nível empresa/Apple Pro Max

class Mostrar:
    """Node para mostrar valores na saída"""
    def __init__(self, valor):
        self.valor = valor

class Guardar:
    """Node para guardar valores em variáveis"""
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

class Repetir:
    """Node para repetir um bloco de código N vezes"""
    def __init__(self, vezes, bloco):
        self.vezes = vezes
        self.bloco = bloco

class Enquanto:
    """Node para loops while/Enquanto"""
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco

class Condicao:
    """Node para if simples"""
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco

class SeSenao:
    """Node para if/else"""
    def __init__(self, condicao, bloco_true, bloco_false):
        self.condicao = condicao
        self.bloco_true = bloco_true
        self.bloco_false = bloco_false

class Funcao:
    """Node para definir funções"""
    def __init__(self, nome, parametros, bloco):
        self.nome = nome
        self.parametros = parametros
        self.bloco = bloco

class Retorna:
    """Node para retornar valores de funções"""
    def __init__(self, valor):
        self.valor = valor

class ChamadaFuncao:
    """Node para chamar funções definidas"""
    def __init__(self, nome, parametros=None):
        self.nome = nome
        self.parametros = parametros or []

class BreakLoop:
    """Node para sair de loops"""
    pass

class ContinueLoop:
    """Node para continuar próximo ciclo de loops"""
    pass

class Lista:
    """Node para criar listas"""
    def __init__(self, elementos):
        self.elementos = elementos

class Dicionario:
    """Node para criar dicionários"""
    def __init__(self, elementos: dict):
        self.elementos = elementos

class AtribuicaoLista:
    """Node para alterar valor em lista por índice"""
    def __init__(self, lista_nome, indice, valor):
        self.lista_nome = lista_nome
        self.indice = indice
        self.valor = valor

class AtribuicaoDicionario:
    """Node para alterar valor em dicionário por chave"""
    def __init__(self, dicio_nome, chave, valor):
        self.dicio_nome = dicio_nome
        self.chave = chave
        self.valor = valor

class ImportModulo:
    """Node para importar módulos seguros"""
    def __init__(self, modulo_nome):
        self.modulo_nome = modulo_nome

class Expressao:
    """Node para expressões complexas"""
    def __init__(self, expressao):
        self.expressao = expressao
