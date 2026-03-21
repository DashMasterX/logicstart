import time
from security import validar_nome, MAX_LOOP
from errors import LogicStartErro

class Executor:
    def __init__(self):
        self.vars = {}
        self.inicio = time.time()
        self.TIMEOUT = 5  # segundos

    def verificar_timeout(self):
        if time.time() - self.inicio > self.TIMEOUT:
            raise LogicStartErro("Tempo de execução excedido")

    def executar(self, ast):
        for node in ast:
            self.verificar_timeout()
            self.exec_node(node)

    def exec_node(self, node):
        if node.__class__.__name__ == "Mostrar":
            print(self.resolver(node.valor))

        elif node.__class__.__name__ == "Guardar":
            if not validar_nome(node.nome):
                raise LogicStartErro(f"Nome inválido: {node.nome}")

            valor = self.resolver(node.valor)
            self.vars[node.nome] = valor

        elif node.__class__.__name__ == "Repetir":
            if node.vezes > MAX_LOOP:
                raise LogicStartErro("Loop excede limite de segurança")

            for _ in range(node.vezes):
                self.executar(node.bloco)

    def resolver(self, valor):
        valor = valor.strip()

        if valor.startswith('"') and valor.endswith('"'):
            return valor[1:-1]

        if valor.isdigit():
            return int(valor)

        if valor.replace('.', '', 1).isdigit():
            return float(valor)

        if valor in self.vars:
            return self.vars[valor]

        raise LogicStartErro(f"Valor inválido: {valor}")