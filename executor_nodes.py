# executor_nodes.py - Executor LogicStart Elite nível empresa
from nodes import (
    Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao,
    Funcao, Retorna, ChamadaFuncao, BreakLoop, ContinueLoop,
    Lista, Dicionario, AtribuicaoLista, AtribuicaoDicionario, Expressao
)
from errors import LogicStartErro

class ExecutorNodes:
    """
    Executor completo de nodes do LogicStart Elite.
    Suporta:
    - Variáveis, funções, loops, condicionais
    - Listas e dicionários
    - Expressões complexas
    """
    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto_global = {}
        self.funcoes = {}
        self.saida = []

    def executar(self):
        self._executar_bloco(self.nodes, self.contexto_global)
        return "\n".join(self.saida) or "✔ Executado com sucesso"

    def _executar_bloco(self, bloco, contexto):
        i = 0
        while i < len(bloco):
            node = bloco[i]

            # Guardar variável
            if isinstance(node, Guardar):
                valor = self._avaliar(node.valor, contexto)
                # Transformar Lista e Dicionario do parser em objetos Python reais
                if isinstance(valor, Lista):
                    contexto[node.nome] = [self._avaliar(x, contexto) for x in valor.elementos]
                elif isinstance(valor, Dicionario):
                    contexto[node.nome] = {k: self._avaliar(v, contexto) for k,v in valor.elementos.items()}
                else:
                    contexto[node.nome] = valor

            # Mostrar
            elif isinstance(node, Mostrar):
                valor = self._avaliar(node.valor, contexto)
                self.saida.append(str(valor))
                print(valor)

            # Repetir N vezes
            elif isinstance(node, Repetir):
                for _ in range(node.vezes):
                    try:
                        self._executar_bloco(node.bloco, contexto.copy())
                    except BreakLoop:
                        break
                    except ContinueLoop:
                        continue

            # Enquanto
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

            # Função
            elif isinstance(node, Funcao):
                self.funcoes[node.nome] = node

            # Chamada de função
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
                    resultado = self._executar_bloco(func.bloco, novo_contexto)
                    # Retorna valor se houver
                    if resultado is not None:
                        return resultado
                except Retorna as r:
                    return r.valor

            # Retorna
            elif isinstance(node, Retorna):
                valor = self._avaliar(node.valor, contexto)
                raise Retorna(valor)

            # Break / Continue
            elif isinstance(node, BreakLoop):
                raise BreakLoop()
            elif isinstance(node, ContinueLoop):
                raise ContinueLoop()

            # Alteração em lista
            elif isinstance(node, AtribuicaoLista):
                lst = contexto.get(node.lista_nome)
                if not isinstance(lst, list):
                    raise LogicStartErro(f"{node.lista_nome} não é uma lista")
                idx = int(self._avaliar(node.indice, contexto))
                lst[idx] = self._avaliar(node.valor, contexto)

            # Alteração em dicionário
            elif isinstance(node, AtribuicaoDicionario):
                d = contexto.get(node.dicio_nome)
                if not isinstance(d, dict):
                    raise LogicStartErro(f"{node.dicio_nome} não é um dicionário")
                chave = self._avaliar(node.chave, contexto)
                d[chave] = self._avaliar(node.valor, contexto)

            # Expressões simples
            elif isinstance(node, Expressao):
                self._avaliar(node.expressao, contexto)

            else:
                raise LogicStartErro(f"Node desconhecido: {node}")

            i += 1

    def _avaliar(self, expr, contexto):
        # Retorna valores simples
        if isinstance(expr, (int,float,bool)):
            return expr

        # Se for string, pode ser variável ou expressão
        if isinstance(expr, str):
            expr = expr.strip()
            # Substitui variáveis conhecidas
            for var in contexto:
                expr = re.sub(rf'\b{var}\b', str(contexto[var]), expr)
            try:
                # Avaliação segura
                return eval(expr, {"__builtins__": {}}, {})
            except:
                return expr.strip('"').strip("'")
        return expr

    def _avaliar_condicao(self, condicao, contexto):
        return bool(self._avaliar(condicao, contexto))
