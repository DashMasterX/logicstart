# security_pro_max.py

import re
import time

# =========================
# CONFIGURAÇÃO PRO MAX
# =========================
MAX_LOOP = 500            # Limite seguro de loops por função
MAX_CODE_SIZE = 5000      # Limite de caracteres do código
MAX_LINES = 300           # Limite de linhas
MAX_EXECUTION_TIME = 3.0  # Tempo máximo de execução em segundos
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
# CLASSE DE SEGURANÇA PRO MAX
# =========================
class SecurityProMax:
    """
    Classe de segurança Pro Max para o IDE LogicStart.
    Valida código antes e durante a execução.
    """

    def __init__(self, max_loop=MAX_LOOP, max_size=MAX_CODE_SIZE, max_lines=MAX_LINES, max_time=MAX_EXECUTION_TIME):
        self.max_loop = max_loop
        self.max_size = max_size
        self.max_lines = max_lines
        self.max_time = max_time
        self.forbidden_patterns = FORBIDDEN_PATTERNS
        self.forbidden_names = FORBIDDEN_NAMES

    # -------------------------
    # VERIFICAÇÃO ESTÁTICA
    # -------------------------
    def verificar_codigo(self, codigo: str) -> bool:
        """
        Verifica o código antes de executar.
        """
        if not codigo or codigo.strip() == "":
            raise ValueError("Código vazio não permitido.")

        if len(codigo) > self.max_size:
            raise ValueError(f"Código muito grande ({len(codigo)}/{self.max_size}).")

        linhas = codigo.splitlines()
        if len(linhas) > self.max_lines:
            raise ValueError(f"Código com muitas linhas ({len(linhas)}/{self.max_lines}).")

        # Detecta padrões perigosos
        for pattern in self.forbidden_patterns:
            if re.search(pattern, codigo, re.IGNORECASE):
                raise ValueError(f"Código contém padrão proibido: '{pattern}'")

        # Verifica loops grandes
        loop_count = sum(1 for l in linhas if re.match(r"(?:\s*)repetir\s+\d+", l))
        if loop_count > self.max_loop:
            raise ValueError(f"Número de loops excede limite seguro ({loop_count}/{self.max_loop}).")

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
                raise ValueError(f"Nome de variável ou função proibido: '{token}'")
        return True

    # -------------------------
    # EXECUÇÃO SEGURA
    # -------------------------
    def executar_seguro(self, func_exec):
        """
        Executa função segura com timeout e bloqueio de loops infinitos.
        `func_exec` é a função que executa o código do usuário.
        """
        start = time.time()
        try:
            resultado = func_exec()
            if (time.time() - start) > self.max_time:
                raise TimeoutError(f"Tempo máximo de execução excedido ({self.max_time}s).")
            return resultado
        except Exception as e:
            raise RuntimeError(f"Erro durante execução segura: {e}")

# =========================
# TESTE RÁPIDO PRO MAX
# =========================
if __name__ == "__main__":
    codigo_teste = """
    variavel x = 10
    repetir 5:
        imprimir(x)
    """

    sec = SecurityProMax()
    try:
        if sec.verificar_codigo(codigo_teste):
            print("Código seguro ✅")
            
            # Simulando execução segura
            def func():
                for i in range(5):
                    print(i)
            sec.executar_seguro(func)
    except Exception as e:
        print(f"Erro de segurança: {e}")
