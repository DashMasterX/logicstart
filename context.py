class Context:
    def __init__(self):
        self.vars = {}

    def set(self, nome, valor):
        self.vars[nome] = valor

    def get(self, nome):
        if nome not in self.vars:
            raise Exception(f"Variável '{nome}' não definida")
        return self.vars[nome]