# lexer.py
import re

class Token:
    def __init__(self, tipo, valor, linha, coluna):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha
        self.coluna = coluna

    def __repr__(self):
        return f"Token({self.tipo}, {self.valor}, {self.linha}:{self.coluna})"

class Lexer:
    PALAVRAS_RESERVADAS = {
        "var": "VAR",
        "const": "CONST",
        "se": "IF",
        "senao": "ELSE",
        "enquanto": "WHILE",
        "imprimir": "PRINT",
        "funcao": "FUNCTION",
        "retornar": "RETURN",
        "verdadeiro": "TRUE",
        "falso": "FALSE",
        "null": "NULL",
    }

    TOKEN_SPEC = [
        ("NUM",       r"\d+(\.\d+)?"),
        ("ID",        r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("OP",        r"==|!=|>=|<=|>|<|\+|\-|\*|/|%|e|ou"),
        ("ASSIGN",    r"="),
        ("LPAREN",    r"\("),
        ("RPAREN",    r"\)"),
        ("LBRACE",    r"\{"),
        ("RBRACE",    r"\}"),
        ("SEMI",      r";"),
        ("COMMA",     r","),
        ("STRING",    r'"[^"]*"'),
        ("NEWLINE",   r"\n"),
        ("SKIP",      r"[ \t]+"),
        ("MISMATCH",  r"."),
    ]

    def __init__(self, codigo):
        self.codigo = codigo
        self.linha = 1
        self.coluna = 1
        self.tokens = []

    def gerar_tokens(self):
        tok_regex = "|".join(f"(?P<{name}>{regex})" for name, regex in self.TOKEN_SPEC)
        for mo in re.finditer(tok_regex, self.codigo):
            tipo = mo.lastgroup
            valor = mo.group()
            if tipo == "NEWLINE":
                self.linha += 1
                self.coluna = 1
                continue
            elif tipo == "SKIP":
                self.coluna += len(valor)
                continue
            elif tipo == "ID" and valor in self.PALAVRAS_RESERVADAS:
                tipo = self.PALAVRAS_RESERVADAS[valor]
            elif tipo == "MISMATCH":
                raise RuntimeError(f"Token inválido {valor} na linha {self.linha}")
            self.tokens.append(Token(tipo, valor, self.linha, self.coluna))
            self.coluna += len(valor)
        return self.tokens
