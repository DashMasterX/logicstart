# parser.py
from lexer import Lexer, Token
from errors import LogicStartErro

class Node:
    """
    Nó da AST
    """
    def __init__(self, tipo, valor=None, filhos=None):
        self.tipo = tipo
        self.valor = valor
        self.filhos = filhos if filhos else []

    def __repr__(self):
        return f"<Node {self.tipo}: {self.valor} filhos={len(self.filhos)}>"

class Parser:
    """
    Parser profissional para LogicStart
    """
    def __init__(self, codigo):
        self.lexer = Lexer(codigo)
        self.tokens = self.lexer.tokenizar()
        self.pos = 0

    # =========================
    # Funções auxiliares
    # =========================
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", "EOF")

    def advance(self):
        self.pos += 1

    def expect(self, tipo):
        token = self.current()
        if token.tipo != tipo:
            raise LogicStartErro(f"Esperado {tipo}, encontrado {token.tipo} ({token.valor}) na linha {token.linha}")
        self.advance()
        return token

    # =========================
    # Função principal
    # =========================
    def parse(self):
        nodes = []
        while self.current().tipo != "EOF":
            nodes.append(self.statement())
        return nodes

    # =========================
    # Statements (comandos)
    # =========================
    def statement(self):
        token = self.current()
        if token.tipo == "VARIAVEL" or token.tipo == "CONSTANTE":
            return self.declaracao()
        elif token.tipo == "FUNÇÃO":
            return self.funcao()
        elif token.tipo == "SE":
            return self.condicional()
        elif token.tipo == "ENQUANTO":
            return self.loop_enquanto()
        elif token.tipo == "IMPRIMIR":
            return self.imprimir()
        else:
            return self.expressao_statement()

    # =========================
    # Declaração de variáveis
    # =========================
    def declaracao(self):
        tipo_token = self.current()
        self.advance()
        nome_token = self.expect("IDENTIFICADOR")
        valor = None
        if self.current().tipo == "OPERADOR" and self.current().valor == "=":
            self.advance()
            valor = self.expressao()
        return Node("DECLARACAO", tipo_token.tipo.lower(), [Node("NOME", nome_token.valor), valor] if valor else [Node("NOME", nome_token.valor)])

    # =========================
    # Função
    # =========================
    def funcao(self):
        self.advance()  # pular "função"
        nome = self.expect("IDENTIFICADOR")
        self.expect("ABRE_PAREN")
        parametros = []
        while self.current().tipo != "FECHA_PAREN":
            param = self.expect("IDENTIFICADOR")
            parametros.append(Node("PARAM", param.valor))
            if self.current().tipo == "VIRGULA":
                self.advance()
        self.expect("FECHA_PAREN")
        corpo = self.bloco()
        return Node("FUNCAO", nome.valor, parametros + corpo)

    # =========================
    # Condicional
    # =========================
    def condicional(self):
        self.advance()  # pular "se"
        condicao = self.expressao()
        corpo = self.bloco()
        filhos = [condicao] + corpo
        if self.current().tipo == "SENÃO":
            self.advance()
            else_c = self.bloco()
            filhos += else_c
        return Node("CONDICIONAL", None, filhos)

    # =========================
    # Loop enquanto
    # =========================
    def loop_enquanto(self):
        self.advance()  # pular "enquanto"
        condicao = self.expressao()
        corpo = self.bloco()
        return Node("ENQUANTO", None, [condicao] + corpo)

    # =========================
    # Imprimir
    # =========================
    def imprimir(self):
        self.advance()  # pular "imprimir"
        self.expect("ABRE_PAREN")
        expr = self.expressao()
        self.expect("FECHA_PAREN")
        return Node("IMPRIMIR", None, [expr])

    # =========================
    # Bloco de código
    # =========================
    def bloco(self):
        self.expect("ABRE_CHAVE")
        nodes = []
        while self.current().tipo != "FECHA_CHAVE":
            nodes.append(self.statement())
        self.expect("FECHA_CHAVE")
        return nodes

    # =========================
    # Expressão
    # =========================
    def expressao_statement(self):
        node = self.expressao()
        return Node("EXPRESSAO", None, [node])

    def expressao(self):
        # Para simplificar, apenas números, strings e identificadores
        token = self.current()
        if token.tipo in ("NUMERO", "STRING", "IDENTIFICADOR"):
            self.advance()
            return Node("VALOR", token.valor)
        elif token.tipo == "VERDADEIRO":
            self.advance()
            return Node("VALOR", True)
        elif token.tipo == "FALSO":
            self.advance()
            return Node("VALOR", False)
        elif token.tipo == "NULO":
            self.advance()
            return Node("VALOR", None)
        else:
            raise LogicStartErro(f"Expressão inválida: {token.tipo} ({token.valor}) na linha {token.linha}")
