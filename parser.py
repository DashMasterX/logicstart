# parser.py

import re
from nodes import Mostrar, Guardar, Repetir, Condicao, Funcao, Retorna
from errors import LogicStartErro

class Parser:
    def __init__(self, codigo: str):
        self.codigo = codigo.splitlines()
        self.pos = 0

    def parse(self):
        """
        Converte o código em uma lista de nodes.
        """
        nodes = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].strip()
            if not linha or linha.startswith("//"):
                self.pos += 1
                continue

            node = self.parse_linha(linha)
            if node:
                nodes.append(node)
            self.pos += 1
        return nodes

    def parse_linha(self, linha):
        # Guardar variável: variavel x = 10
        match_var = re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha)
        if match_var:
            nome, valor = match_var.groups()
            return Guardar(nome, valor)

        # Mostrar: mostrar("texto")
        match_mostrar = re.match(r'^mostrar\((.+)\)$', linha)
        if match_mostrar:
            valor = match_mostrar.group(1)
            return Mostrar(valor)

        # Loop: repetir 5
        match_loop = re.match(r'^repetir\s+(\d+)$', linha)
        if match_loop:
            vezes = int(match_loop.group(1))
            self.pos += 1
            bloco = self.parse_bloco("fim repetir")
            return Repetir(vezes, bloco)

        # Condicional: se x > 5
        match_se = re.match(r'^se\s+(.+)$', linha)
        if match_se:
            condicao = match_se.group(1)
            self.pos += 1
            bloco_verdadeiro = self.parse_bloco("fim se")
            return Condicao(condicao, bloco_verdadeiro)

        # Função: funcao nome(param1, param2)
        match_func = re.match(r'^funcao\s+(\w+)\((.*?)\)$', linha)
        if match_func:
            nome, params = match_func.groups()
            parametros = [p.strip() for p in params.split(",") if p.strip()]
            self.pos += 1
            bloco = self.parse_bloco("fim funcao")
            return Funcao(nome, parametros, bloco)

        # Retorna: retorna x
        match_retorna = re.match(r'^retorna\s+(.+)$', linha)
        if match_retorna:
            valor = match_retorna.group(1)
            return Retorna(valor)

        raise LogicStartErro(f"Comando desconhecido: '{linha}'")

    def parse_bloco(self, fim_comando):
        """
        Captura todas as linhas até o comando de término (fim repetir, fim se, fim funcao)
        """
        bloco = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].strip()
            if linha.lower() == fim_comando:
                return bloco
            node = self.parse_linha(linha)
            if node:
                bloco.append(node)
            self.pos += 1
        raise LogicStartErro(f"Bloco não fechado. Esperado: '{fim_comando}'")
