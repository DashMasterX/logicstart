# security.py

import re

# =========================
# CONFIGURAÇÃO
# =========================
MAX_LOOP = 1000          # Limite de loops
MAX_CODE_SIZE = 5000     # Limite de caracteres
FORBIDDEN_PATTERNS = [
    r"import\s+os",
    r"import\s+sys",
    r"import\s+subprocess",
    r"eval\(",
    r"exec\(",
    r"open\(",
    r"__import__\(",
    r"while\s+True",
    r"for\s+.*\s+in\s+range\(\s*1000000",  # Loop gigante
]

# =========================
# CLASSE DE SEGURANÇA
# =========================
class Security:
    """
    Classe de segurança para validar código LogicStart.
    """

    def __init__(self, max_loop=MAX_LOOP, max_size=MAX_CODE_SIZE):
        self.max_loop = max_loop
        self.max_size = max_size
        self.forbidden_patterns = FORBIDDEN_PATTERNS

    def verificar(self, codigo: str) -> bool:
        """
        Retorna True se o código estiver seguro. Lança ValueError se inválido.
        """
        if not codigo:
            raise ValueError("Código vazio não permitido")

        if len(codigo) > self.max_size:
            raise ValueError(f"Código muito grande ({len(codigo)}/{self.max_size})")

        # Verifica padrões proibidos
        for pattern in self.forbidden_patterns:
            if re.search(pattern, codigo, re.IGNORECASE):
                raise ValueError(f"Código contém padrão proibido: '{pattern}'")

        # Verifica loops excessivos
        loop_count = sum(1 for l in codigo.splitlines() if re.match(r"(?:\s*)repetir\s+\d+", l))
        if loop_count > self.max_loop:
            raise ValueError(f"Número de loops excede limite seguro ({loop_count}/{self.max_loop})")

        # Verifica nomes de variáveis/funções
        return validar_nome(codigo)


# =========================
# FUNÇÃO VALIDAR NOMES
# =========================
def validar_nome(codigo: str) -> bool:
    """
    Verifica se os nomes de variáveis/funções não utilizam palavras reservadas ou perigosas.
    """
    forbidden_names = ["import", "exec", "eval", "os", "sys", "subprocess", "open", "__import__"]
    tokens = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", codigo)
    for token in tokens:
        if token.lower() in forbidden_names:
            raise ValueError(f"Nome de variável ou função proibido: '{token}'")
    return True
