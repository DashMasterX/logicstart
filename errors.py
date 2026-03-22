# erros.py

class LogicStartErro(Exception):
    """Erro genérico da engine LogicStart"""
    def __init__(self, mensagem: str):
        super().__init__(mensagem)
        self.mensagem = mensagem

class LogicStartSintaxeErro(LogicStartErro):
    """Erro de sintaxe no código LogicStart"""
    def __init__(self, linha: int, mensagem: str):
        super().__init__(f"Sintaxe inválida na linha {linha}: {mensagem}")
        self.linha = linha

class LogicStartExecucaoErro(LogicStartErro):
    """Erro durante a execução do código LogicStart"""
    def __init__(self, linha: int, mensagem: str):
        super().__init__(f"Erro de execução na linha {linha}: {mensagem}")
        self.linha = linha

class LogicStartSegurancaErro(LogicStartErro):
    """Erro de segurança ao validar código"""
    def __init__(self, mensagem: str):
        super().__init__(f"Violação de segurança: {mensagem}")
