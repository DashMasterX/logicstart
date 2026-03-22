# executor_nodes.py - Executor nível empresa/Apple Pro Max

from nodes import (
    Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao,
    Funcao, Retorna, ChamadaFuncao, BreakLoop, ContinueLoop,
    Lista, Dicionario, AtribuicaoLista, AtribuicaoDicionario,
    Expressao
)
from errors import LogicStartErro

class ExecutorNodes:
    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto = {}      # Variáveis globais
        self.funcoes = {}       # Funções definidas
        self.saida = []         # Saída de 'Mostrar'
        self._loop_break = False
        self._loop_continue = False

    def executar(self):
        """Executa todos os nodes"""
        for node in self.nodes:
            self.executar_node(node)
        return "\n".join(self.saida) or "✔ Executado com sucesso"

    def executar_node(self, node):
        """Executa um único node de acordo com seu tipo"""
        if isinstance(node, Guardar):
            self.contexto[node.nome] = self.avaliar_expressao(node.valor)

        elif isinstance(node, Mostrar):
            valor = self.avaliar_expressao(node.valor)
            self.saida.append(str(valor))
            print(valor)

        elif isinstance(node, Repetir):
            for _ in range(node.vezes):
                for n in node.bloco:
                    self.executar_node(n)
                    if self._loop_break:
                        self._loop_break = False
                        return
                    if self._loop_continue:
                        self._loop_continue = False
                        break

        elif isinstance(node, Enquanto):
            while self.avaliar_condicao(node.condicao):
                for n in node.bloco:
                    self.executar_node(n)
                    if self._loop_break:
                        self._loop_break = False
                        return
                    if self._loop_continue:
                        self._loop_continue = False
                        break

        elif isinstance(node, Condicao):
            if self.avaliar_condicao(node.condicao):
                for n in node.bloco:
                    self.executar_node(n)

        elif isinstance(node, SeSenao):
            bloco = node.bloco_true if self.avaliar_condicao(node.condicao) else node.bloco_false
            for n in bloco:
                self.executar_node(n)

        elif isinstance(node, Funcao):
            self.funcoes[node.nome] = node

        elif isinstance(node, ChamadaFuncao):
            if node.nome not in self.funcoes:
                raise LogicStartErro(f"Função '{node.nome}' não definida")
            func = self.funcoes[node.nome]
            if len(func.parametros) != len(node.parametros):
                raise LogicStartErro(f"Parâmetros incorretos para '{node.nome}'")
            # Contexto temporário para função
            old_contexto = self.contexto.copy()
            for p, v in zip(func.parametros, node.parametros):
                self.contexto[p] = self.avaliar_expressao(v)
            for n in func.bloco:
                self.executar_node(n)
            self.contexto = old_contexto

        elif isinstance(node, Retorna):
            valor = self.avaliar_expressao(node.valor)
            self.saida.append(str(valor))
            print(valor)

        elif isinstance(node, BreakLoop):
            self._loop_break = True

        elif isinstance(node, ContinueLoop):
            self._loop_continue = True

        elif isinstance(node, Lista):
            return [self.avaliar_expressao(v) for v in node.elementos]

        elif isinstance(node, Dicionario):
            return {k: self.avaliar_expressao(v) for k, v in node.elementos.items()}

        elif isinstance(node, AtribuicaoLista):
            if node.lista_nome not in self.contexto:
                raise LogicStartErro(f"Lista '{node.lista_nome}' não existe")
            self.contexto[node.lista_nome][node.indice] = self.avaliar_expressao(node.valor)

        elif isinstance(node, AtribuicaoDicionario):
            if node.dicio_nome not in self.contexto:
                raise LogicStartErro(f"Dicionário '{node.dicio_nome}' não existe")
            self.contexto[node.dicio_nome][node.chave] = self.avaliar_expressao(node.valor)

        elif isinstance(node, Expressao):
            return self.avaliar_expressao(node.expressao)

        else:
            raise LogicStartErro(f"Node desconhecido: {node}")

    def avaliar_expressao(self, expr):
        """Avalia expressões usando variáveis do contexto"""
        try:
            if isinstance(expr, str):
                for var in self.contexto:
                    expr = expr.replace(var, str(self.contexto[var]))
                return eval(expr, {}, {})
            return expr
        except Exception:
            return expr
       
    def avaliar_condicao(self, cond):
        """Avalia condições booleanas"""
        try:
            if isinstance(cond, str):
                for var in self.contexto:
                    cond = cond.replace(var, str(self.contexto[var]))
                return bool(eval(cond, {}, {}))
            return bool(cond)
        except Exception:
            return False
