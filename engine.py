# engine.py - LogicStart Engine Profissional Nível Steam
import re
from errors import LogicStartErro

class LogicStart:
    def __init__(self, codigo):
        self.codigo = codigo
        self.variaveis = {}  # memória de variáveis
        self.funcoes = {}    # memória de funções
        self.saida = []

    def executar(self):
        linhas = self.codigo.split("\n")
        for i, linha in enumerate(linhas, 1):
            linha = linha.strip()
            if not linha or linha.startswith("//"):
                continue
            try:
                self._executar_linha(linha)
            except Exception as e:
                raise LogicStartErro(f"Erro na linha {i}: {linha}\n{e}")

    def _executar_linha(self, linha):
        # =========================
        # imprimir("texto")
        # =========================
        match = re.match(r'imprimir\((.*)\)', linha)
        if match:
            valor = self._avaliar(match.group(1))
            print(valor)
            self.saida.append(str(valor))
            return

        # =========================
        # declaração de variáveis
        # =========================
        match = re.match(r'(variavel|constante)\s+([a-zA-Z_]\w*)\s*=\s*(.+)', linha)
        if match:
            _, nome, expr = match.groups()
            self.variaveis[nome] = self._avaliar(expr)
            return

        # =========================
        # atribuição simples
        # =========================
        match = re.match(r'([a-zA-Z_]\w*)\s*=\s*(.+)', linha)
        if match:
            nome, expr = match.groups()
            if nome not in self.variaveis:
                raise LogicStartErro(f"Variável não declarada: {nome}")
            self.variaveis[nome] = self._avaliar(expr)
            return

        # =========================
        # funções simples
        # =========================
        match = re.match(r'função\s+([a-zA-Z_]\w*)\s*\(\)\s*\{', linha)
        if match:
            nome = match.group(1)
            # placeholder para funções futuras
            self.funcoes[nome] = "função"
            return

        # =========================
        # comandos lógicos básicos (placeholder)
        # =========================
        if linha in ["pare", "fim"]:
            return

        raise LogicStartErro(f"Comando desconhecido: {linha}")

    def _avaliar(self, expr):
        # substitui variáveis pelo valor
        for var in self.variaveis:
            expr = re.sub(r'\b{}\b'.format(var), str(self.variaveis[var]), expr)
        # operadores lógicos em português
        expr = expr.replace("e", "and").replace("ou", "or").replace("não", "not")
        # avalia expressão com segurança
        try:
            return eval(expr, {"__builtins__": {}})
        except Exception as e:
            raise LogicStartErro(f"Erro ao avaliar expressão: {expr}\n{e}")
