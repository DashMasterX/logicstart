# executor.py
from engine import LogicStart
from security import validar_nome, MAX_LOOP

class Executor:
    def __init__(self, codigo: str):
        self.codigo = codigo.strip()
        self.logic = None

    def validar(self):
        """
        Valida nomes de variáveis e funções, tamanho do código e loops
        """
        if len(self.codigo) > MAX_LOOP:
            raise ValueError(f"Código muito grande, limite {MAX_LOOP} caracteres")
        
        # Verifica nomes inválidos
        linhas = self.codigo.splitlines()
        for linha in linhas:
            tokens = linha.replace("(", " ").replace(")", " ").split()
            for t in tokens:
                if not validar_nome(t) and t.isidentifier():
                    raise ValueError(f"Nome inválido detectado: {t}")

        return True

    def executar(self):
        """
        Executa o código através do engine LogicStart
        """
        if not self.codigo:
            raise ValueError("Nenhum código enviado")

        # Validação de segurança
        self.validar()

        # Inicializa engine
        self.logic = LogicStart(self.codigo)

        try:
            self.logic.executar()
        except Exception as e:
            raise RuntimeError(f"Erro durante execução: {e}")

        # Retorna resultado
        return self.logic.get_output()
