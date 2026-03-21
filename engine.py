import re
from errors import LogicStartErro

class LogicStart:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.variaveis = {}  # Armazena variáveis
        self.funcoes = {}    # Armazena funções
        self.saida = []

    def executar(self):
        linhas = self.codigo.splitlines()
        for linha in linhas:
            linha = linha.strip()
            if not linha or linha.startswith("//"):  # Ignora comentários
                continue
            self.processar_linha(linha)

    def processar_linha(self, linha):
        try:
            # Variável: variavel x = 10
            var_match = re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha)
            if var_match:
                nome, valor = var_match.groups()
                self.variaveis[nome] = self.avaliar_expressao(valor)
                return

            # Imprimir: imprimir("Olá")
            imprimir_match = re.match(r'^imprimir\((.+)\)$', linha)
            if imprimir_match:
                valor = self.avaliar_expressao(imprimir_match.group(1))
                self.saida.append(str(valor))
                print(valor)
                return

            # Condicional simples: se x > 5
            se_match = re.match(r'^se\s+(.+)$', linha)
            if se_match:
                condicao = se_match.group(1)
                if not self.avaliar_condicao(condicao):
                    # Ignora linha seguinte
                    return
                return

            # Retorna valor: retorna x
            retorna_match = re.match(r'^retorna\s+(.+)$', linha)
            if retorna_match:
                valor = self.avaliar_expressao(retorna_match.group(1))
                self.saida.append(str(valor))
                print(valor)
                return

            # Outros comandos ainda não implementados
            raise LogicStartErro(f"Comando desconhecido: {linha}")

        except Exception as e:
            raise LogicStartErro(f"Erro ao processar linha '{linha}': {e}")

    def avaliar_expressao(self, expr):
        # Substitui variáveis
        for var in self.variaveis:
            expr = re.sub(r'\b' + var + r'\b', str(self.variaveis[var]), expr)
        # Avalia expressões matemáticas simples
        try:
            return eval(expr, {}, {})
        except:
            return expr.strip('"').strip("'")

    def avaliar_condicao(self, cond):
        # Substitui variáveis
        for var in self.variaveis:
            cond = re.sub(r'\b' + var + r'\b', str(self.variaveis[var]), cond)
        try:
            return bool(eval(cond, {}, {}))
        except:
            return False
