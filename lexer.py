# lexer.py
import re
from errors import LogicStartErro

class Token:
    def __init__(self, tipo, valor, linha=0, coluna=0):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"<Token {self.tipo}: {self.valor} ({self.linha}:{self.coluna})>"

class Lexer:
    """
    Lexer profissional para a linguagem LogicStart (português)
    """

    # Palavras-chave da linguagem
    PALAVRAS_CHAVE = {
        "variavel", "constante", "função", "retorna",
        "se", "senão", "enquanto", "para", "imprimir",
        "verdadeiro", "falso", "nulo", "e", "ou", "não"
    }

    # Expressões regulares para tokenização
    TOKEN_REGEX = [
        ("NUMERO", r"\d+(\.\d+)?"),
        ("STRING", r"\".*?\"|'.*?'"),
        ("IDENTIFICADOR", r"[A-Za-z_][A-Za-z0-9_]*"),
        ("OPERADOR", r"[\+\-\*/%=<>!]+"),
        ("PONTO", r"\."),
        ("VIRGULA", r","),
        ("DOIS_PONTOS", r":"),
        ("ABRE_PAREN", r"\("),
        ("FECHA_PAREN", r"\)"),
        ("ABRE_CHAVE", r"\{"),
        ("FECHA_CHAVE", r"\}"),
        ("ESPACO", r"\s+"),
        ("COMENTARIO", r"#.*?$"),
    ]

    def __init__(self, codigo):
        self.codigo = codigo
        self.pos = 0
        self.linha = 1
        self.coluna = 1
        self.tokens = []

    def tokenizar(self):
        codigo = self.codigo
        while self.pos < len(codigo):
            match = None
            for tipo, regex in self.TOKEN_REGEX:
                pattern = re.compile(regex, re.MULTILINE)
                match = pattern.match(codigo, self.pos)
                if match:
                    texto = match.group(0)
                    if tipo == "IDENTIFICADOR" and texto in self.PALAVRAS_CHAVE:
                        tipo = texto.upper()
                    if tipo not in ("ESPACO", "COMENTARIO"):
                        self.tokens.append(Token(tipo, texto, self.linha, self.coluna))
                    linhas = texto.count("\n")
                    if linhas:
                        self.linha += linhas
                        self.coluna = len(texto.rsplit("\n", 1)[-1]) + 1
                    else:
                        self.coluna += len(texto)
                    self.pos = match.end()
                    break
            if not match:
                raise LogicStartErro(f"Caractere inválido: '{codigo[self.pos]}' na linha {self.linha}, coluna {self.coluna}")
        return self.tokens
