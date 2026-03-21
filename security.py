# security.py

import re

# =========================
# CONFIGURAÇÃO DE SEGURANÇA
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
    r"for\s+.*\s+in\s+range\(\s*1000000",  # Loop grande demais
]


class Security:
    """
    Classe de segurança para validar código LogicStart antes da execução.
    """

    def __init__(self, max_loop=MAX_LOOP, max_size=MAX_CODE_SIZE):
        self.max_loop = max_loop
        self.max_size = max_size
        self.forbidden_patterns = FORBIDDEN_PATTERNS

    def verificar(self, codigo: str) -> bool:
        """
        Valida o código. Retorna True se seguro, lança ValueError se bloqueado.
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

        # Verifica nomes inválidos
        tokens = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", codigo)
        forbidden_names = ["import", "exec", "eval", "os", "sys", "subprocess"]
        for t in tokens:
            if t.lower() in forbidden_names:
                raise ValueError(f"Nome de variável ou função proibido: '{t}'")

        return True
