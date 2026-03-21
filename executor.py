# executor.py
from parser import Node
from errors import LogicStartErro

class Escopo:
    """
    Gerencia variáveis locais e globais
    """
    def __init__(self, pai=None):
        self.vars = {}
        self.pai = pai

    def definir(self, nome, valor):
        self.vars[nome] = valor

    def obter(self, nome):
        if nome in self.vars:
            return self.vars[nome]
        elif self.pai:
            return self.pai.obter(nome)
        else:
            raise LogicStartErro(f"Variável '{nome}' não definida")

class Executor:
    """
    Executa os nodes da AST gerados pelo parser
    """
    def __init__(self):
        self.escopo_global = Escopo()
        self.output = []

    def executar(self, nodo: Node, escopo=None):
        if escopo is None:
            escopo = self.escopo_global

        metodo = f"_exec_{nodo.tipo}"
        if hasattr(self, metodo):
            return getattr(self, metodo)(nodo, escopo)
        else:
            # Nodo genérico percorre filhos
            resultado = None
            for filho in nodo.filhos:
                resultado = self.executar(filho, escopo)
            return resultado

    # =========================
    # Programa
    # =========================
    def _exec_PROGRAMA(self, nodo, escopo):
        for stmt in nodo.filhos:
            self.executar(stmt, escopo)

    # =========================
    # Bloco
    # =========================
    def _exec_BLOCO(self, nodo, escopo):
        novo_escopo = Escopo(pai=escopo)
        for stmt in nodo.filhos:
            resultado = self.executar(stmt, novo_escopo)
            # Suporte a retorno de função
            if resultado is not None:
                return resultado

    # =========================
    # Variáveis
    # =========================
    def _exec_VAR(self, nodo, escopo):
        nome = nodo.valor
        valor = self.executar(nodo.filhos[0], escopo) if nodo.filhos else None
        escopo.definir(nome, valor)

    def _exec_CONST(self, nodo, escopo):
        nome = nodo.valor
        valor = self.executar(nodo.filhos[0], escopo) if nodo.filhos else None
        escopo.definir(nome, valor)

    # =========================
    # Impressão
    # =========================
    def _exec_IMPRIMIR(self, nodo, escopo):
        valor = self.executar(nodo.filhos[0], escopo)
        self.output.append(str(valor))
        print(valor)
        return valor

    # =========================
    # Literais
    # =========================
    def _exec_NUMERO(self, nodo, escopo):
        return float(nodo.valor) if '.' in nodo.valor else int(nodo.valor)

    def _exec_STRING(self, nodo, escopo):
        return nodo.valor[1:-1]  # remove aspas

    def _exec_TRUE(self, nodo, escopo):
        return True

    def _exec_FALSE(self, nodo, escopo):
        return False

    def _exec_NULL(self, nodo, escopo):
        return None

    def _exec_IDENTIFICADOR(self, nodo, escopo):
        return escopo.obter(nodo.valor)

    # =========================
    # Condicionais
    # =========================
    def _exec_SE(self, nodo, escopo):
        condicao = self.executar(nodo.filhos[0], escopo)
        if condicao:
            return self.executar(nodo.filhos[1], escopo)
        elif len(nodo.filhos) > 2:
            return self.executar(nodo.filhos[2], escopo)

    # =========================
    # Loops enquanto
    # =========================
    def _exec_ENQUANTO(self, nodo, escopo):
        while self.executar(nodo.filhos[0], escopo):
            resultado = self.executar(nodo.filhos[1], escopo)
            if resultado is not None:
                return resultado

    # =========================
    # Funções
    # =========================
    def _exec_FUNÇÃO(self, nodo, escopo):
        nome = nodo.valor
        escopo.definir(nome, nodo)  # armazena node da função

    def _exec_RETORNA(self, nodo, escopo):
        return self.executar(nodo.filhos[0], escopo) if nodo.filhos else None
