# contexto.py

class Contexto:
    """
    Classe de contexto para armazenar variáveis da sessão LogicStart.
    Suporta escopo global e local, com métodos de inspeção.
    """

    def __init__(self):
        self.global_vars = {}
        self.local_stack = []

    # ======================
    # Escopo Global
    # ======================
    def definir_global(self, nome, valor):
        """Define uma variável global"""
        self.global_vars[nome] = valor

    def obter_global(self, nome):
        if nome not in self.global_vars:
            raise Exception(f"Variável global '{nome}' não definida")
        return self.global_vars[nome]

    # ======================
    # Escopo Local
    # ======================
    def abrir_escopo(self):
        """Abre um novo escopo local"""
        self.local_stack.append({})

    def fechar_escopo(self):
        """Fecha o escopo local atual"""
        if not self.local_stack:
            raise Exception("Não há escopo local para fechar")
        self.local_stack.pop()

    def definir_local(self, nome, valor):
        """Define uma variável no escopo local atual"""
        if not self.local_stack:
            raise Exception("Não há escopo local ativo")
        self.local_stack[-1][nome] = valor

    def obter_local(self, nome):
        """Obtém uma variável do escopo local ou global"""
        for escopo in reversed(self.local_stack):
            if nome in escopo:
                return escopo[nome]
        if nome in self.global_vars:
            return self.global_vars[nome]
        raise Exception(f"Variável '{nome}' não definida")

    # ======================
    # Métodos de inspeção
    # ======================
    def listar_variaveis(self):
        """Retorna todas as variáveis locais e globais"""
        resultado = {}
        for escopo in self.local_stack:
            resultado.update(escopo)
        resultado.update(self.global_vars)
        return resultado

    def existe(self, nome):
        """Verifica se a variável existe em algum escopo"""
        for escopo in reversed(self.local_stack):
            if nome in escopo:
                return True
        return nome in self.global_vars
