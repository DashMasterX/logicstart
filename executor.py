# executor_nodes.py

from nodes import Mostrar, Guardar, Repetir, Condicao, Funcao, Retorna
from errors import LogicStartErro

class ExecutorNodes:
    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto = {}       # Variáveis globais
        self.funcoes = {}        # Funções definidas
        self.saida = []          # Armazena saída de 'mostrar'

    def executar(self):
        for node in self.nodes:
            self.executar_node(node)
        return "\n".join(self.saida) or "✔ Executado com sucesso"

    def executar_node(self, node):
        if isinstance(node, Guardar):
            valor = self.avaliar_expressao(node.valor)
            self.contexto[node.nome] = valor

        elif isinstance(node, Mostrar):
            valor = self.avaliar_expressao(node.valor)
            self.saida.append(str(valor))
            print(valor)

        elif isinstance(node, Repetir):
            for _ in range(node.vezes):
                for n in node.bloco:
                    self.executar_node(n)

        elif isinstance(node, Condicao):
            if self.avaliar_condicao(node.condicao):
                for n in node.bloco:
                    self.executar_node(n)

        elif isinstance(node, Funcao):
            self.funcoes[node.nome] = node

        elif isinstance(node, Retorna):
            valor = self.avaliar_expressao(node.valor)
            self.saida.append(str(valor))
            print(valor)

        else:
            raise LogicStartErro(f"Node desconhecido: {node}")

    def avaliar_expressao(self, expr):
        """
        Avalia expressões simples usando variáveis do contexto.
        """
        try:
            # Substitui variáveis
            for var in self.contexto:
                expr = expr.replace(var, str(self.contexto[var]))
            # Avalia matemática simples
            return eval(expr, {}, {})
        except:
            # Retorna string literal se não for expressão matemática
            return expr.strip('"').strip("'")

    def avaliar_condicao(self, cond):
        """
        Avalia condições como se x > 5
        """
        try:
            for var in self.contexto:
                cond = cond.replace(var, str(self.contexto[var]))
            return bool(eval(cond, {}, {}))
        except:
            return False
