# security.py - Executor de segurança LogicStart Pro Max

import re
import time
from errors import LogicStartErro

# =========================
# CONFIGURAÇÃO
# =========================
MAX_LOOP = 500
MAX_CODE_SIZE = 5000
MAX_LINES = 300
MAX_EXECUTION_TIME = 3.0

FORBIDDEN_PATTERNS = [
    r"import\s+os",
    r"import\s+sys",
    r"import\s+subprocess",
    r"eval\(",
    r"exec\(",
    r"open\(",
    r"__import__\(",
    r"while\s+True",
    r"for\s+.*\s+in\s+range\(\s*1000000",
]

FORBIDDEN_NAMES = [
    "import", "exec", "eval", "os", "sys", "subprocess", "open", "__import__"
]

# =========================
# CLASSE DE SEGURANÇA
# =========================
class Security:
    """
    Classe de segurança LogicStart.
    Valida código antes e durante a execução.
    """

    def __init__(self):
        self.max_loop = MAX_LOOP
        self.max_size = MAX_CODE_SIZE
        self.max_lines = MAX_LINES
        self.max_time = MAX_EXECUTION_TIME
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        self.forbidden_names = FORBIDDEN_NAMES

    # -------------------------
    # VERIFICAÇÃO ESTÁTICA
    # -------------------------
    def verificar(self, codigo: str):
        """
        Verifica o código antes de executar.
        Levanta LogicStartErro se detectar problema.
        """
        if not codigo or codigo.strip() == "":
            raise LogicStartErro("Código vazio não permitido.")

        if len(codigo) > self.max_size:
            raise LogicStartErro(f"Código muito grande ({len(codigo)}/{self.max_size}).")

        linhas = codigo.splitlines()
        if len(linhas) > self.max_lines:
            raise LogicStartErro(f"Código com muitas linhas ({len(linhas)}/{self.max_lines}).")

        # Detecta padrões perigosos
        for pattern in self.forbidden_patterns:
            if re.search(pattern, codigo, re.IGNORECASE):
                raise LogicStartErro(f"Código contém padrão proibido: '{pattern}'")

        # Conta loops
        loop_count = sum(1 for l in linhas if re.match(r"(?:\s*)repetir\s+\d+", l))
        if loop_count > self.max_loop:
            raise LogicStartErro(f"Número de loops excede limite seguro ({loop_count}/{self.max_loop}).")

        # Valida nomes de variáveis/funções
        self.validar_nomes(codigo)

        return True

    # -------------------------
    # VALIDA NOMES
    # -------------------------
    def validar_nomes(self, codigo: str):
        tokens = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\b", codigo)
        for token in tokens:
            if token.lower() in self.forbidden_names:
                raise LogicStartErro(f"Nome de variável ou função proibido: '{token}'")
        return True

    # -------------------------
    # EXECUÇÃO SEGURA
    # -------------------------
    def executar_seguro(self, func_exec):
        """
        Executa função segura com timeout.
        """
        start = time.time()
        try:
            resultado = func_exec()
            if (time.time() - start) > self.max_time:
                raise LogicStartErro(f"Tempo máximo de execução excedido ({self.max_time}s).")
            return resultado
        except Exception as e:
            raise LogicStartErro(f"Erro durante execução segura: {e}")


# =========================
# TESTE RÁPIDO
# =========================
if __name__ == "__main__":
    codigo_teste = """
    variavel x = 10
    repetir 5:
        mostrar(x)
    """

    sec = Security()
    try:
        if sec.verificar(codigo_teste):
            print("Código seguro ✅")

            # Simulando execução segura
            def func():
                for i in range(5):
                    print(i)

            sec.executar_seguro(func)
    except Exception as e:
        print(f"Erro de segurança: {e}")
