# parser_novo.py

import re
from nodes import (
    Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao,
    Funcao, Retorna, ChamadaFuncao, Lista, Dicionario, AtribuicaoLista,
    AtribuicaoDicionario, Expressao
)
from errors import LogicStartErro

class ParserNovo:
    def __init__(self, codigo: str):
        self.codigo = codigo.splitlines()
        self.pos = 0

    def parse(self):
        nodes = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].split("//")[0].strip()
            if not linha:
                self.pos += 1
                continue
            node = self.parse_linha(linha)
            if node:
                nodes.append(node)
            self.pos += 1
        return nodes

    def parse_linha(self, linha):
        linha = linha.strip()
        # Guardar variável
        match_var = re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha, re.IGNORECASE)
        if match_var:
            nome, valor = match_var.groups()
            return Guardar(nome, valor.strip())

        # Mostrar / imprimir
        match_mostrar = re.match(r'^mostrar\((.+)\)$', linha, re.IGNORECASE)
        if match_mostrar:
            valor = match_mostrar.group(1).strip()
            return Mostrar(valor)

        # Repetir loop
        match_loop = re.match(r'^repetir\s+(\d+)$', linha, re.IGNORECASE)
        if match_loop:
            vezes = int(match_loop.group(1))
            self.pos += 1
            bloco = self.parse_bloco("fim repetir")
            return Repetir(vezes, bloco)

        # Enquanto
        match_enquanto = re.match(r'^enquanto\s+(.+)$', linha, re.IGNORECASE)
        if match_enquanto:
            condicao = match_enquanto.group(1).strip()
            self.pos += 1
            bloco = self.parse_bloco("fim enquanto")
            return Enquanto(condicao, bloco)

        # Condicional simples
        match_se = re.match(r'^se\s+(.+)$', linha, re.IGNORECASE)
        if match_se:
            condicao = match_se.group(1).strip()
            self.pos += 1
            bloco_verdadeiro = self.parse_bloco("fim se")
            return Condicao(condicao, bloco_verdadeiro)

        # Condicional com else
        match_senao = re.match(r'^se\s+(.+)\s+senao$', linha, re.IGNORECASE)
        if match_senao:
            condicao = match_senao.group(1).strip()
            self.pos += 1
            bloco_true = self.parse_bloco("senao")
            self.pos += 1
            bloco_false = self.parse_bloco("fim se")
            return SeSenao(condicao, bloco_true, bloco_false)

        # Função
        match_func = re.match(r'^funcao\s+(\w+)\((.*?)\)$', linha, re.IGNORECASE)
        if match_func:
            nome, params = match_func.groups()
            parametros = [p.strip() for p in params.split(",") if p.strip()]
            self.pos += 1
            bloco = self.parse_bloco("fim funcao")
            return Funcao(nome, parametros, bloco)

        # Chamada de função
        match_call = re.match(r'^chamar\s+(\w+)\((.*?)\)$', linha, re.IGNORECASE)
        if match_call:
            nome, params = match_call.groups()
            parametros = [p.strip() for p in params.split(",") if p.strip()]
            return ChamadaFuncao(nome, parametros)

        # Retorna
        match_retorna = re.match(r'^retorna\s+(.+)$', linha, re.IGNORECASE)
        if match_retorna:
            return Retorna(match_retorna.group(1).strip())

        # Lista: lista x = [1,2,3]
        match_lista = re.match(r'^lista\s+(\w+)\s*=\s*\[(.*)\]$', linha, re.IGNORECASE)
        if match_lista:
            nome, elementos = match_lista.groups()
            elementos = [e.strip() for e in elementos.split(",") if e.strip()]
            return Guardar(nome, Lista(elementos))

        # Dicionário: dicio y = {a:1,b:2}
        match_dicio = re.match(r'^dicio\s+(\w+)\s*=\s*\{(.+)\}$', linha, re.IGNORECASE)
        if match_dicio:
            nome, conteudo = match_dicio.groups()
            elementos = {}
            for par in conteudo.split(","):
                if ":" in par:
                    k,v = par.split(":",1)
                    elementos[k.strip()] = v.strip()
            return Guardar(nome, Dicionario(elementos))

        # Atribuição de lista: x[0] = 10
        match_atr_list = re.match(r'^(\w+)\[(.+)\]\s*=\s*(.+)$', linha)
        if match_atr_list:
            nome, idx, valor = match_atr_list.groups()
            return AtribuicaoLista(nome.strip(), idx.strip(), valor.strip())

        # Atribuição de dicionário: y["chave"] = valor
        match_atr_dic = re.match(r'^(\w+)\[(.+)\]\s*=\s*(.+)$', linha)
        if match_atr_dic:
            nome, chave, valor = match_atr_dic.groups()
            return AtribuicaoDicionario(nome.strip(), chave.strip(), valor.strip())

        # Expressão simples
        return Expressao(linha)
    
    def parse_bloco(self, fim_comando):
        fim_comando = fim_comando.lower()
        bloco = []
        while self.pos < len(self.codigo):
            linha = self.codigo[self.pos].split("//")[0].strip()
            if linha.lower() == fim_comando:
                return bloco
            node = self.parse_linha(linha)
            if node:
                bloco.append(node)
            self.pos += 1
        raise LogicStartErro(f"Bloco não fechado. Esperado: '{fim_comando}'")
