# nodes.py

class Mostrar:
    """
    Representa um comando de saída (imprimir) no código LogicStart.
    """
    def __init__(self, valor):
        self.valor = valor


class Guardar:
    """
    Representa uma declaração de variável (guardar/variavel) no código LogicStart.
    """
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor


class Repetir:
    """
    Representa um loop no código LogicStart.
    `vezes` -> número de repetições
    `bloco` -> lista de nós (comandos) dentro do loop
    """
    def __init__(self, vezes, bloco):
        self.vezes = vezes
        self.bloco = bloco


class Condicao:
    """
    Representa uma condicional (se/então/senão) no código LogicStart.
    `condicao` -> expressão a ser avaliada
    `bloco_verdadeiro` -> lista de comandos se True
    `bloco_falso` -> lista de comandos se False (opcional)
    """
    def __init__(self, condicao, bloco_verdadeiro, bloco_falso=None):
        self.condicao = condicao
        self.bloco_verdadeiro = bloco_verdadeiro
        self.bloco_falso = bloco_falso or []


class Funcao:
    """
    Representa uma função no código LogicStart.
    `nome` -> nome da função
    `parametros` -> lista de nomes de parâmetros
    `bloco` -> lista de comandos dentro da função
    """
    def __init__(self, nome, parametros, bloco):
        self.nome = nome
        self.parametros = parametros
        self.bloco = bloco


class Retorna:
    """
    Representa um comando de retorno de valor (retorna) no código LogicStart.
    """
    def __init__(self, valor):
        self.valor = valor
