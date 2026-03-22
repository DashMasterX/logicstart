# executor_nodes.py

from nodes import Mostrar, Guardar, Repetir, Condicao, Funcao, Retorna, Enquanto, SeSenao
from errors import LogicStartErro

class ExecutorNodes:
    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto_global = {}    # Variáveis globais
        self.funcoes = {}            # Funções definidas
        self.saida = []              # Armazena saída de 'mostrar'

    # -----------------------------
    # Executa todos os nodes
    # -----------------------------
    def executar(self):
        for node in self.nodes:
            self.executar_node(node, self.contexto_global)
        return "\n".join(self.saida) or "✔ Executado com sucesso"

    # -----------------------------
    # Executa um único node
    # -----------------------------
    def executar_node(self, node, contexto):
        if isinstance(node, Guardar):
            valor = self.avaliar_expressao(node.valor, contexto)
            contexto[node.nome] = valor

        elif isinstance(node, Mostrar):
            valor = self.avaliar_expressao(node.valor, contexto)
            self.saida.append(str(valor))
            print(valor)

        elif isinstance(node, Repetir):
            vezes = self.avaliar_expressao(node.vezes, contexto)
            for _ in range(int(vezes)):
                for n in node.bloco:
                    self.executar_node(n, contexto.copy())

        elif isinstance(node, Enquanto):
            while self.avaliar_condicao(node.condicao, contexto):
                for n in node.bloco:
                    self.executar_node(n, contexto.copy())

        elif isinstance(node, Condicao):
            if self.avaliar_condicao(node.condicao, contexto):
                for n in node.bloco:
                    self.executar_node(n, contexto.copy())

        elif isinstance(node, SeSenao):
            if self.avaliar_condicao(node.condicao, contexto):
                for n in node.bloco_true:
                    self.executar_node(n, contexto.copy())
            else:
                for n in node.bloco_false:
                    self.executar_node(n, contexto.copy())

        elif isinstance(node, Funcao):
            self.funcoes[node.nome] = node

        elif isinstance(node, Retorna):
            valor = self.avaliar_expressao(node.valor, contexto)
            raise RetornoFuncao(valor)

        elif isinstance(node, ChamadaFuncao):
            self.executar_funcao(node.nome, node.parametros, contexto)

        else:
            raise LogicStartErro(f"Node desconhecido: {node}")

    # -----------------------------
    # Avalia expressões
    # -----------------------------
    def avaliar_expressao(self, expr, contexto):
        try:
            # Substitui variáveis do contexto
            for var in contexto:
                expr = expr.replace(var, repr(contexto[var]))
            # Substitui funções chamadas
            for f in self.funcoes:
                expr = expr.replace(f"chamar({f})", f"self.executar_funcao('{f}', [], contexto)")
            # Avaliação segura usando eval limitado
            return eval(expr, {"__builtins__": {}}, {})
        except Exception:
            # Retorna string literal se não for expressão matemática
            return expr.strip('"').strip("'")

    # -----------------------------
    # Avalia condições
    # -----------------------------
    def avaliar_condicao(self, cond, contexto):
        try:
            for var in contexto:
                cond = cond.replace(var, repr(contexto[var]))
            return bool(eval(cond, {"__builtins__": {}}, {}))
        except Exception:
            return False

    # -----------------------------
    # Executa função
    # -----------------------------
    def executar_funcao(self, nome, parametros, contexto_chamador):
        if nome not in self.funcoes:
            raise LogicStartErro(f"Função '{nome}' não definida")
        func = self.funcoes[nome]
        contexto_local = contexto_chamador.copy()
        # Associa parâmetros
        for i, p in enumerate(parametros):
            if i < len(func.parametros):
                contexto_local[func.parametros[i]] = p
        try:
            for n in func.bloco:
                self.executar_node(n, contexto_local)
        except RetornoFuncao as r:
            return r.valor
        return None

# -----------------------------
# Exceção interna de retorno
# -----------------------------
class RetornoFuncao(Exception):
    def __init__(self, valor):
        self.valor = valor
