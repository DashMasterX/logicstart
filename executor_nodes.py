# executor_nodes.py - Executor LogicStart Elite nível empresa

from nodes import (
    Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao,
    Funcao, Retorna, ChamadaFuncao, BreakLoop, ContinueLoop,
    Lista, Dicionario, AtribuicaoLista, AtribuicaoDicionario, Expressao
)
from errors import LogicStartErro

class ExecutorNodes:
    """
    Executor dos nodes do LogicStart.
    Suporta variáveis, funções, loops, listas, dicionários e expressões.
    """

    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto_global = {}    # Variáveis globais
        self.funcoes = {}            # Funções definidas
        self.saida = []              # Saída de 'mostrar'

    def executar(self):
        """
        Executa todos os nodes fornecidos.
        """
        self._executar_bloco(self.nodes, self.contexto_global)
        return "\n".join(self.saida) or "✔ Executado com sucesso"

    def _executar_bloco(self, bloco, contexto):
        i = 0
        while i < len(bloco):
            node = bloco[i]

            # Guardar variável
            if isinstance(node, Guardar):
                contexto[node.nome] = self._avaliar(node.valor, contexto)

            # Mostrar saída
            elif isinstance(node, Mostrar):
                valor = self._avaliar(node.valor, contexto)
                self.saida.append(str(valor))
                print(valor)

            # Repetir bloco N vezes
            elif isinstance(node, Repetir):
                for _ in range(node.vezes):
                    try:
                        self._executar_bloco(node.bloco, contexto.copy())
                    except BreakLoop:
                        break
                    except ContinueLoop:
                        continue

            # Enquanto / Loop while
            elif isinstance(node, Enquanto):
                while self._avaliar_condicao(node.condicao, contexto):
                    try:
                        self._executar_bloco(node.bloco, contexto.copy())
                    except BreakLoop:
                        break
                    except ContinueLoop:
                        continue

            # Condicional simples
            elif isinstance(node, Condicao):
                if self._avaliar_condicao(node.condicao, contexto):
                    self._executar_bloco(node.bloco, contexto.copy())

            # Condicional com else
            elif isinstance(node, SeSenao):
                if self._avaliar_condicao(node.condicao, contexto):
                    self._executar_bloco(node.bloco_true, contexto.copy())
                else:
                    self._executar_bloco(node.bloco_false, contexto.copy())

            # Definir função
            elif isinstance(node, Funcao):
                self.funcoes[node.nome] = node

            # Chamar função
            elif isinstance(node, ChamadaFuncao):
                if node.nome not in self.funcoes:
                    raise LogicStartErro(f"Função '{node.nome}' não definida")
                func = self.funcoes[node.nome]
                if len(node.parametros) != len(func.parametros):
                    raise LogicStartErro(f"Parâmetros incorretos para '{node.nome}'")
                novo_contexto = contexto.copy()
                for nome_param, valor_param in zip(func.parametros, node.parametros):
                    novo_contexto[nome_param] = self._avaliar(valor_param, contexto)
                try:
                    self._executar_bloco(func.bloco, novo_contexto)
                except Retorna as r:
                    return r.valor

            # Retorna de função
            elif isinstance(node, Retorna):
                valor = self._avaliar(node.valor, contexto)
                raise Retorna(valor)

            # Controle de loops
            elif isinstance(node, BreakLoop):
                raise BreakLoop()
            elif isinstance(node, ContinueLoop):
                raise ContinueLoop()

            # Listas
            elif isinstance(node, Lista):
                return [self._avaliar(x, contexto) for x in node.elementos]

            # Dicionários
            elif isinstance(node, Dicionario):
                return {k: self._avaliar(v, contexto) for k, v in node.elementos.items()}

            # Alterar valor de lista
            elif isinstance(node, AtribuicaoLista):
                lst = contexto.get(node.lista_nome)
                if not isinstance(lst, list):
                    raise LogicStartErro(f"{node.lista_nome} não é uma lista")
                idx = self._avaliar(node.indice, contexto)
                lst[idx] = self._avaliar(node.valor, contexto)

            # Alterar valor de dicionário
            elif isinstance(node, AtribuicaoDicionario):
                d = contexto.get(node.dicio_nome)
                if not isinstance(d, dict):
                    raise LogicStartErro(f"{node.dicio_nome} não é um dicionário")
                chave = self._avaliar(node.chave, contexto)
                d[chave] = self._avaliar(node.valor, contexto)

            # Expressões complexas
            elif isinstance(node, Expressao):
                self._avaliar(node.expressao, contexto)

            else:
                raise LogicStartErro(f"Node desconhecido: {node}")

            i += 1

    def _avaliar(self, expr, contexto):
        """
        Avalia expressões simples ou complexas com variáveis do contexto.
        """
        if isinstance(expr, (int, float, bool)):
            return expr

        if isinstance(expr, str):
            # Substituir variáveis no contexto
            for var in contexto:
                expr = expr.replace(var, str(contexto[var]))
            try:
                # Avalia de forma segura
                return eval(expr, {"__builtins__": {}}, {})
            except:
                # Retorna como string se não for expressão
                return expr.strip('"').strip("'")

        return expr

    def _avaliar_condicao(self, condicao, contexto):
        """
        Avalia condições retornando True ou False.
        """
        return bool(self._avaliar(condicao, contexto))
