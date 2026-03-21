# parser.py
from lexer import Token

class Node:
    def __init__(self, tipo, valor=None, filhos=None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = filhos or []

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        nodes = []
        while self.pos < len(self.tokens):
            nodes.append(self._declaracao())
        return nodes

    def _declaracao(self):
        token = self.tokens[self.pos]
        if token.tipo in ("VAR", "CONST"):
            return self._var_const()
        elif token.tipo == "IMPRIMIR":
            return self._imprimir()
        elif token.tipo == "IF":
            return self._if()
        elif token.tipo == "WHILE":
            return self._while()
        else:
            return self._expressao()

    def _var_const(self):
        tipo = self.tokens[self.pos].tipo.lower()
        self.pos += 1
        nome = self.tokens[self.pos].valor
        self.pos += 1
        valor = None
        if self.tokens[self.pos].tipo == "ASSIGN":
            self.pos += 1
            valor = self._expressao()
        if self.tokens[self.pos].tipo == "SEMI":
            self.pos += 1
        return Node("DECLARACAO", tipo, [Node("NOME", nome), valor] if valor else [Node("NOME", nome)])

    def _imprimir(self):
        self.pos += 1
        if self.tokens[self.pos].tipo != "LPAREN":
            raise RuntimeError("Esperado '(' após imprimir")
        self.pos += 1
        expr = self._expressao()
        if self.tokens[self.pos].tipo != "RPAREN":
            raise RuntimeError("Esperado ')' após imprimir")
        self.pos += 1
        if self.tokens[self.pos].tipo == "SEMI":
            self.pos += 1
        return Node("IMPRIMIR", filhos=[expr])

    def _expressao(self):
        token = self.tokens[self.pos]
        self.pos += 1
        if token.tipo == "NUM":
            return Node("VALOR", float(token.valor))
        elif token.tipo == "STRING":
            return Node("VALOR", token.valor.strip('"'))
        elif token.tipo == "ID":
            return Node("NOME", token.valor)
        else:
            return Node("VALOR", token.valor)  # fallback simples

    def _if(self):
        # Implementar condicional profissional
        pass

    def _while(self):
        # Implementar loop enquanto profissional
        pass
