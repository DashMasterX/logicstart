# parser.py
from lexer import Lexer, Token
from errors import LogicStartErro

class Node:
    def __init__(self, tipo, valor=None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = []

    def adicionar(self, node):
        self.filhos.append(node)

    def __repr__(self):
        if self.valor:
            return f"{self.tipo}({self.valor})"
        return f"{self.tipo}({self.filhos})"

class Parser:
    def __init__(self, codigo):
        self.tokens = Lexer(codigo).tokenizar()
        self.posicao = 0

    def parse(self):
        programa = Node("PROGRAMA")
        while self.posicao < len(self.tokens):
            stmt = self.declaracao()
            if stmt:
                programa.adicionar(stmt)
        return programa

    def declaracao(self):
        token = self._atual()
        if token.tipo in ("VAR", "CONST"):
            return self.variavel()
        elif token.tipo == "FUNÇÃO":
            return self.funcao()
        elif token.tipo == "IMPRIMIR":
            return self.imprimir()
        elif token.tipo == "SE":
            return self.condicional()
        elif token.tipo == "ENQUANTO":
            return self.enquanto()
        else:
            self._avancar()
            return None

    # =============================
    # Declaração de variáveis
    # =============================
    def variavel(self):
        tipo = self._atual().tipo
        self._avancar()
        nome = self._expect("IDENTIFICADOR").valor
        valor = None
        if self._aceitar("OPERADOR", "="):
            valor = self.expressao()
        self._expect("PONTUACAO", ";")
        node = Node(tipo, nome)
        if valor:
            node.adicionar(valor)
        return node

    # =============================
    # Funções
    # =============================
    def funcao(self):
        self._avancar()
        nome = self._expect("IDENTIFICADOR").valor
        self._expect("PONTUACAO", "(")
        self._expect("PONTUACAO", ")")
        corpo = self.bloco()
        node = Node("FUNÇÃO", nome)
        node.adicionar(corpo)
        return node

    # =============================
    # Condicionais
    # =============================
    def condicional(self):
        self._avancar()
        cond = self.expressao()
        corpo = self.bloco()
        node = Node("SE")
        node.adicionar(cond)
        node.adicionar(corpo)
        if self._aceitar("SENÃO"):
            corpo_else = self.bloco()
            node.adicionar(corpo_else)
        return node

    # =============================
    # Loops
    # =============================
    def enquanto(self):
        self._avancar()
        cond = self.expressao()
        corpo = self.bloco()
        node = Node("ENQUANTO")
        node.adicionar(cond)
        node.adicionar(corpo)
        return node

    # =============================
    # Impressão
    # =============================
    def imprimir(self):
        self._avancar()
        valor = self.expressao()
        self._expect("PONTUACAO", ";")
        node = Node("IMPRIMIR")
        node.adicionar(valor)
        return node

    # =============================
    # Bloco
    # =============================
    def bloco(self):
        self._expect("PONTUACAO", "{")
        bloco = Node("BLOCO")
        while not self._aceitar("PONTUACAO", "}"):
            stmt = self.declaracao()
            if stmt:
                bloco.adicionar(stmt)
        return bloco

    # =============================
    # Expressões simples
    # =============================
    def expressao(self):
        token = self._atual()
        if token.tipo == "NUMERO":
            self._avancar()
            return Node("NUMERO", token.valor)
        elif token.tipo == "STRING":
            self._avancar()
            return Node("STRING", token.valor)
        elif token.tipo in ("TRUE", "FALSE", "NULL"):
            self._avancar()
            return Node(token.tipo)
        else:
            self._avancar()
            return Node("IDENTIFICADOR", token.valor)

    # =============================
    # Funções auxiliares
    # =============================
    def _atual(self):
        if self.posicao < len(self.tokens):
            return self.tokens[self.posicao]
        return Token("EOF", None, -1, -1)

    def _avancar(self):
        self.posicao += 1

    def _expect(self, tipo, valor=None):
        token = self._atual()
        if token.tipo != tipo or (valor and token.valor != valor):
            raise LogicStartErro(f"Esperado {tipo}('{valor}') mas encontrou {token.tipo}('{token.valor}') na linha {token.linha}")
        self._avancar()
        return token

    def _aceitar(self, tipo, valor=None):
        token = self._atual()
        if token.tipo == tipo and (valor is None or token.valor == valor):
            self._avancar()
            return True
        return False
