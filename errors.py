# errors.py - Erros LogicStart nível empresa/Apple Pro Max

class LogicStartErro(Exception):
    """Erro genérico do LogicStart"""
    def __init__(self, mensagem):
        super().__init__(f"[LogicStartErro] {mensagem}")

class ParserErro(LogicStartErro):
    """Erro durante o parsing do código"""
    def __init__(self, linha, mensagem):
        super().__init__(f"Erro no parser na linha '{linha}': {mensagem}")
        self.linha = linha

class VariavelNaoDefinidaErro(LogicStartErro):
    """Erro quando uma variável não foi definida"""
    def __init__(self, nome):
        super().__init__(f"Variável não definida: '{nome}'")
        self.nome = nome

class FuncaoNaoDefinidaErro(LogicStartErro):
    """Erro quando uma função não foi definida"""
    def __init__(self, nome):
        super().__init__(f"Função não definida: '{nome}'")
        self.nome = nome

class TipoInvalidoErro(LogicStartErro):
    """Erro de tipo inválido em operação ou atribuição"""
    def __init__(self, esperado, recebido):
        super().__init__(f"Tipo inválido: esperado '{esperado}', recebido '{recebido}'")
        self.esperado = esperado
        self.recebido = recebido

class LoopExcedidoErro(LogicStartErro):
    """Erro quando um loop excede limite seguro"""
    def __init__(self, limite):
        super().__init__(f"Loop excedeu limite seguro de {limite} iterações")
        self.limite = limite

class AtribuicaoErro(LogicStartErro):
    """Erro ao atribuir valor a variável/lista/dicionário"""
    def __init__(self, alvo, valor):
        super().__init__(f"Não foi possível atribuir valor '{valor}' ao alvo '{alvo}'")
        self.alvo = alvo
        self.valor = valor
