# engine.py

import re
from contexto import Contexto
from security import Security

class LogicStartErro(Exception):
    pass

class Engine:
    """
    Engine LogicStart Pro Max
    Suporta Python em português com escopos, funções, variáveis e segurança.
    """

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.contexto = Contexto()
        self.saida = []
        self.security = Security()

    def executar(self):
        # Verifica segurança antes
        try:
            self.security.verificar(self.codigo)
        except ValueError as e:
            raise LogicStartErro(f"Erro de segurança: {e}")

        linhas = self.codigo.splitlines()
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue
            i += self.processar_linha(linha, i, linhas)

    def processar_linha(self, linha, idx, linhas):
        # Variável: variavel x = 10
        var_match = re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha)
        if var_match:
            nome, valor = var_match.groups()
            valor_eval = self.avaliar_expressao(valor)
            self.contexto.definir_local(nome, valor_eval)
            return 1

        # Imprimir: imprimir("Olá")
        imprimir_match = re.match(r'^imprimir\((.+)\)$', linha)
        if imprimir_match:
            valor = self.avaliar_expressao(imprimir_match.group(1))
            self.saida.append(str(valor))
            print(valor)
            return 1

        # Condicional simples: se x > 5
        se_match = re.match(r'^se\s+(.+)$', linha)
        if se_match:
            condicao = se_match.group(1)
            if not self.avaliar_condicao(condicao):
                # Pula próxima linha
                return 2
            return 1

        # Retorna valor: retorna x
        retorna_match = re.match(r'^retorna\s+(.+)$', linha)
        if retorna_match:
            valor = self.avaliar_expressao(retorna_match.group(1))
            self.saida.append(str(valor))
            print(valor)
            return 1

        # Loop: repetir 5
        loop_match = re.match(r'^repetir\s+(\d+)$', linha)
        if loop_match:
            vezes = int(loop_match.group(1))
            # Executa próxima linha X vezes
            proxima = linhas[idx + 1].strip() if idx + 1 < len(linhas) else ""
            for _ in range(vezes):
                self.processar_linha(proxima, idx + 1, linhas)
            return 2

        # Comando desconhecido
        raise LogicStartErro(f"Comando desconhecido: {linha}")

    def avaliar_expressao(self, expr):
        # Substitui variáveis
        tokens = re.findall(r'\b\w+\b', expr)
        for t in tokens:
            if self.contexto.existe(t):
                expr = re.sub(r'\b' + t + r'\b', str(self.contexto.obter_local(t)), expr)
        # Avalia expressões matemáticas
        try:
            return eval(expr, {}, {})
        except:
            return expr.strip('"').strip("'")

    def avaliar_condicao(self, cond):
        # Substitui variáveis
        tokens = re.findall(r'\b\w+\b', cond)
        for t in tokens:
            if self.contexto.existe(t):
                cond = re.sub(r'\b' + t + r'\b', str(self.contexto.obter_local(t)), cond)
        try:
            return bool(eval(cond, {}, {}))
        except:
            return False
