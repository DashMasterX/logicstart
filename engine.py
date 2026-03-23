# engine.py

import re
from contexto import Contexto
from security import Security


class LogicStartErro(Exception):
    pass


class RetornoFuncao(Exception):
    def __init__(self, valor):
        self.valor = valor


class Engine:
    def __init__(self, codigo: str, contexto=None):
        self.codigo = codigo
        self.linhas = codigo.splitlines()
        self.contexto = contexto if contexto else Contexto()
        self.security = Security()
        self.saida = []
        self.i = 0

    # ================= EXECUÇÃO =================

    def executar(self):
        self.security.verificar(self.codigo)

        while self.i < len(self.linhas):
            linha = self._limpar(self.linhas[self.i])

            if not linha:
                self.i += 1
                continue

            try:
                self._executar_linha(linha)
            except RetornoFuncao as r:
                return r.valor
            except LogicStartErro as e:
                raise LogicStartErro(f"Linha {self.i+1}: {e}")

            self.i += 1

    # ================= PARSER =================

    def _limpar(self, linha):
        linha = linha.strip()
        if linha.startswith("//"):
            return ""
        return linha

    def _executar_linha(self, linha):

        # -------- VARIÁVEL --------
        if m := re.match(r'^variavel\s+(\w+)\s*=\s*(.+)$', linha):
            nome, valor = m.groups()
            self.contexto.definir_local(nome, self._eval(valor))
            return

        # -------- PRINT --------
        if m := re.match(r'^imprimir\((.+)\)$', linha):
            valor = self._eval(m.group(1))
            self.saida.append(str(valor))
            print(valor)
            return

        # -------- IF --------
        if m := re.match(r'^se\s+(.+)$', linha):
            cond = self._eval_cond(m.group(1))

            bloco_if, bloco_else, fim = self._capturar_if()

            if cond:
                self._executar_bloco(bloco_if)
            else:
                self._executar_bloco(bloco_else)

            self.i = fim
            return

        # -------- LOOP --------
        if m := re.match(r'^repetir\s+(\d+)$', linha):
            vezes = int(m.group(1))

            bloco, fim = self._capturar_bloco("fim_repetir")

            for _ in range(vezes):
                self._executar_bloco(bloco)

            self.i = fim
            return

        # -------- FUNÇÃO --------
        if m := re.match(r'^funcao\s+(\w+)\((.*)\)$', linha):
            nome, params = m.groups()

            params = [p.strip() for p in params.split(",") if p.strip()]

            bloco, fim = self._capturar_bloco("fim_funcao")

            self.contexto.definir_funcao(nome, params, bloco)

            self.i = fim
            return

        # -------- RETURN --------
        if m := re.match(r'^retorna\s+(.+)$', linha):
            valor = self._eval(m.group(1))
            raise RetornoFuncao(valor)

        # -------- CHAMADA FUNÇÃO --------
        if m := re.match(r'^(\w+)\((.*)\)$', linha):
            self._chamar_funcao(m.group(1), m.group(2))
            return

        raise LogicStartErro(f"Comando inválido: {linha}")

    # ================= BLOCOS =================

    def _capturar_bloco(self, fim_token):
        bloco = []
        i = self.i + 1

        while i < len(self.linhas):
            linha = self._limpar(self.linhas[i])
            if linha == fim_token:
                return bloco, i
            bloco.append(self.linhas[i])
            i += 1

        raise LogicStartErro(f"Esperado '{fim_token}'")

    def _capturar_if(self):
        bloco_if = []
        bloco_else = []
        atual = bloco_if

        i = self.i + 1

        while i < len(self.linhas):
            linha = self._limpar(self.linhas[i])

            if linha == "senao":
                atual = bloco_else
            elif linha == "fim_se":
                return bloco_if, bloco_else, i
            else:
                atual.append(self.linhas[i])

            i += 1

        raise LogicStartErro("if não fechado")

    def _executar_bloco(self, bloco):
        sub = Engine("\n".join(bloco), self.contexto.criar_subcontexto())
        resultado = sub.executar()
        self.saida.extend(sub.saida)
        return resultado

    # ================= EXPRESSÕES =================

    def _eval(self, expr):
        expr = self._substituir_variaveis(expr)

        try:
            return eval(expr, {}, {})
        except:
            return expr.strip('"').strip("'")

    def _eval_cond(self, cond):
        cond = self._substituir_variaveis(cond)

        try:
            return bool(eval(cond, {}, {}))
        except:
            return False

    def _substituir_variaveis(self, texto):
        tokens = re.findall(r'\b\w+\b', texto)

        for t in tokens:
            if self.contexto.existe(t):
                valor = self.contexto.obter_local(t)
                texto = re.sub(r'\b'+t+r'\b', repr(valor), texto)

        return texto

    # ================= FUNÇÕES =================

    def _chamar_funcao(self, nome, args_str):
        if not self.contexto.existe_funcao(nome):
            raise LogicStartErro(f"Função '{nome}' não existe")

        args = []
        if args_str.strip():
            args = [self._eval(a.strip()) for a in args_str.split(",")]

        corpo, params = self.contexto.obter_funcao(nome)

        if len(args) != len(params):
            raise LogicStartErro("Argumentos inválidos")

        novo_contexto = self.contexto.criar_subcontexto()

        for p, a in zip(params, args):
            novo_contexto.definir_local(p, a)

        sub = Engine("\n".join(corpo), novo_contexto)

        try:
            return sub.executar()
        except RetornoFuncao as r:
            return r.valor
