# parser_executor_pro.py

import re
from copy import deepcopy

# -----------------------------
# Nodes
# -----------------------------
class Guardar:
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor

class Mostrar:
    def __init__(self, valor):
        self.valor = valor

class Repetir:
    def __init__(self, vezes, bloco):
        self.vezes = vezes
        self.bloco = bloco

class Enquanto:
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco

class Condicao:
    def __init__(self, condicao, bloco):
        self.condicao = condicao
        self.bloco = bloco

class Funcao:
    def __init__(self, nome, parametros, bloco):
        self.nome = nome
        self.parametros = parametros
        self.bloco = bloco

class Retorna(Exception):
    def __init__(self, valor):
        self.valor = valor

class ChamadaFuncao:
    def __init__(self, nome, parametros):
        self.nome = nome
        self.parametros = parametros

class Expressao:
    def __init__(self, expressao):
        self.expressao = expressao

# -----------------------------
# Parser Pro
# -----------------------------
class ParserExecutorPro:
    def __init__(self, codigo):
        self.codigo = codigo.splitlines()
        self.pos = 0

    def parse(self):
        nodes = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].split("//")[0].strip()
            if linha:
                nodes.append(self.parse_linha(linha))
            self.pos += 1
        return nodes

    def parse_linha(self, linha):
        linha = linha.strip()

        # variavel x = 10
        match_var = re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha, re.IGNORECASE)
        if match_var:
            nome, valor = match_var.groups()
            # Se for chamada de função dentro da atribuição
            match_call = re.match(r'^chamar\s+(\w+)\((.*)\)$', valor.strip())
            if match_call:
                func_nome, params = match_call.groups()
                parametros = [p.strip() for p in params.split(",") if p.strip()]
                return Guardar(nome, ChamadaFuncao(func_nome, parametros))
            return Guardar(nome, valor.strip())

        # mostrar(x)
        match_mostrar = re.match(r'^mostrar\((.+)\)$', linha, re.IGNORECASE)
        if match_mostrar:
            return Mostrar(match_mostrar.group(1).strip())

        # repetir N
        match_repetir = re.match(r'^repetir\s+(\d+)$', linha, re.IGNORECASE)
        if match_repetir:
            vezes = int(match_repetir.group(1))
            self.pos += 1
            bloco = self.parse_bloco("fim repetir")
            return Repetir(vezes, bloco)

        # enquanto condicao
        match_enquanto = re.match(r'^enquanto\s+(.+)$', linha, re.IGNORECASE)
        if match_enquanto:
            condicao = match_enquanto.group(1).strip()
            self.pos += 1
            bloco = self.parse_bloco("fim enquanto")
            return Enquanto(condicao, bloco)

        # se condicao
        match_se = re.match(r'^se\s+(.+)$', linha, re.IGNORECASE)
        if match_se:
            condicao = match_se.group(1).strip()
            self.pos += 1
            bloco = self.parse_bloco("fim se")
            return Condicao(condicao, bloco)

        # funcao nome(param1, param2)
        match_func = re.match(r'^funcao\s+(\w+)\((.*?)\)$', linha, re.IGNORECASE)
        if match_func:
            nome, params = match_func.groups()
            parametros = [p.strip() for p in params.split(",") if p.strip()]
            self.pos += 1
            bloco = self.parse_bloco("fim funcao")
            return Funcao(nome, parametros, bloco)

        # chamar funcao(param1, param2)
        match_call = re.match(r'^chamar\s+(\w+)\((.*)\)$', linha, re.IGNORECASE)
        if match_call:
            nome, params = match_call.groups()
            parametros = [p.strip() for p in params.split(",") if p.strip()]
            return ChamadaFuncao(nome, parametros)

        # retorna x
        match_retorna = re.match(r'^retorna\s+(.+)$', linha, re.IGNORECASE)
        if match_retorna:
            return Retorna(match_retorna.group(1).strip())

        # expressão simples
        return Expressao(linha)

    def parse_bloco(self, fim_comando):
        fim_comando = fim_comando.lower()
        bloco = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].split("//")[0].strip()
            if linha.lower() == fim_comando:
                return bloco
            bloco.append(self.parse_linha(linha))
            self.pos += 1
        raise Exception(f"Bloco não fechado: {fim_comando}")

# -----------------------------
# Executor Pro
# -----------------------------
class ExecutorPro:
    def __init__(self, nodes):
        self.nodes = nodes
        self.contexto = {}
        self.funcoes = {}
        self.saida = []

    def executar(self):
        self._executar_bloco(self.nodes, self.contexto)
        return "\n".join(str(x) for x in self.saida)

    def _executar_bloco(self, bloco, contexto):
        i = 0
        while i < len(bloco):
            node = bloco[i]

            if isinstance(node, Guardar):
                contexto[node.nome] = self._avaliar(node.valor, contexto)

            elif isinstance(node, Mostrar):
                valor = self._avaliar(node.valor, contexto)
                self.saida.append(valor)

            elif isinstance(node, Repetir):
                for _ in range(node.vezes):
                    self._executar_bloco(deepcopy(node.bloco), deepcopy(contexto))

            elif isinstance(node, Enquanto):
                while self._avaliar(node.condicao, contexto):
                    self._executar_bloco(deepcopy(node.bloco), deepcopy(contexto))

            elif isinstance(node, Condicao):
                if self._avaliar(node.condicao, contexto):
                    self._executar_bloco(deepcopy(node.bloco), deepcopy(contexto))

            elif isinstance(node, Funcao):
                self.funcoes[node.nome] = node

            elif isinstance(node, ChamadaFuncao):
                if node.nome not in self.funcoes:
                    raise Exception(f"Função '{node.nome}' não definida")
                func = self.funcoes[node.nome]
                novo_contexto = deepcopy(contexto)
                for nome_param, valor_param in zip(func.parametros, node.parametros):
                    novo_contexto[nome_param] = self._avaliar(valor_param, contexto)
                try:
                    self._executar_bloco(func.bloco, novo_contexto)
                except Retorna as r:
                    return r.valor

            elif isinstance(node, Retorna):
                valor = self._avaliar(node.valor, contexto)
                raise Retorna(valor)

            elif isinstance(node, Expressao):
                self._avaliar(node.expressao, contexto)

            i += 1

    def _avaliar(self, expr, contexto):
        if isinstance(expr, (int, float, bool)):
            return expr
        if isinstance(expr, ChamadaFuncao):
            return self._executar_chamada(expr, contexto)
        if isinstance(expr, str):
            # substituir variáveis
            for var in contexto:
                expr = re.sub(rf'\b{var}\b', str(contexto[var]), expr)
            try:
                return eval(expr, {"__builtins__": {}})
            except:
                return expr
        return expr

    def _executar_chamada(self, chamada, contexto):
        if chamada.nome not in self.funcoes:
            raise Exception(f"Função '{chamada.nome}' não definida")
        func = self.funcoes[chamada.nome]
        novo_contexto = deepcopy(contexto)
        for nome_param, valor_param in zip(func.parametros, chamada.parametros):
            novo_contexto[nome_param] = self._avaliar(valor_param, contexto)
        try:
            self._executar_bloco(func.bloco, novo_contexto)
        except Retorna as r:
            return r.valor
        return None
