# engine.py
from security import Security, MAX_LOOP, validar_nome
from errors import LogicStartErro
import re

class LogicStart:
    """
    Interpretador LogicStart (português estilo JavaScript/Steam)
    """

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.variaveis = {}   # Variáveis globais
        self.funcoes = {}     # Funções definidas
        self.security = Security()

        # Validação de segurança
        if not self.security.verificar(codigo):
            raise LogicStartErro("Código bloqueado por segurança")

    def executar(self):
        """Executa o código principal"""
        self._executar_bloco(self.codigo.splitlines(), self.variaveis)

    # =========================
    # EXECUÇÃO DE BLOCO
    # =========================
    def _executar_bloco(self, linhas, escopo):
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue

            # =========================
            # VARIÁVEIS
            # =========================
            match_var = re.match(r"variavel\s+(\w+)\s*=\s*(.+)", linha)
            if match_var:
                nome, valor = match_var.groups()
                escopo[nome] = self._avaliar_expressao(valor, escopo)
                i += 1
                continue

            # =========================
            # FUNÇÕES
            # =========================
            match_func = re.match(r"funcao\s+(\w+)\((.*)\):", linha)
            if match_func:
                nome, args = match_func.groups()
                bloco = self._capturar_bloco(linhas, i)
                self.funcoes[nome] = (args.split(",") if args.strip() else [], bloco)
                i += len(bloco) + 2
                continue

            # =========================
            # CHAMADA DE FUNÇÃO
            # =========================
            match_call = re.match(r"(\w+)\((.*)\)", linha)
            if match_call and match_call.group(1) in self.funcoes:
                nome, args_str = match_call.groups()
                self._chamar_funcao(nome, args_str, escopo)
                i += 1
                continue

            # =========================
            # MOSTRAR
            # =========================
            match_mostrar = re.match(r"mostrar\s+(.+)", linha)
            if match_mostrar:
                valor = self._avaliar_expressao(match_mostrar.group(1), escopo)
                print(valor)
                i += 1
                continue

            # =========================
            # CONDICIONAL SE / SENAO
            # =========================
            if linha.startswith("se "):
                cond = re.match(r"se\s+(.+):", linha).group(1)
                if self._avaliar_expressao(cond, escopo):
                    i += 1
                    continue
                else:
                    i = self._pular_bloco(linhas, i)
                    continue

            if linha.startswith("senao:"):
                i += 1
                continue

            # =========================
            # LOOP REPETIR
            # =========================
            match_repetir = re.match(r"repetir\s+(\d+)\s+vezes:", linha)
            if match_repetir:
                vezes = int(match_repetir.group(1))
                bloco = self._capturar_bloco(linhas, i)
                for _ in range(vezes):
                    self._executar_bloco(bloco, dict(escopo))
                i += len(bloco) + 2
                continue

            # =========================
            # LOOP ENQUANTO
            # =========================
            match_enquanto = re.match(r"enquanto\s+(.+):", linha)
            if match_enquanto:
                cond = match_enquanto.group(1)
                bloco = self._capturar_bloco(linhas, i)
                loop_count = 0
                while self._avaliar_expressao(cond, escopo):
                    if loop_count > MAX_LOOP:
                        raise LogicStartErro("Loop infinito detectado")
                    self._executar_bloco(bloco, dict(escopo))
                    loop_count += 1
                i += len(bloco) + 2
                continue

            # =========================
            # FIM
            # =========================
            if linha == "fim":
                i += 1
                continue

            raise LogicStartErro(f"Comando desconhecido: {linha}")

    # =========================
    # AVALIAR EXPRESSÃO
    # =========================
    def _avaliar_expressao(self, expr, escopo):
        """
        Avalia expressões aritméticas, strings, booleanos e variáveis.
        """
        # Substitui variáveis pelo valor real
        for nome, valor in escopo.items():
            if isinstance(valor, str):
                valor_str = f'"{valor}"'
            else:
                valor_str = str(valor)
            expr = re.sub(rf"\b{nome}\b", valor_str, expr)

        # Substitui booleanos português
        expr = expr.replace("verdadeiro", "True").replace("falso", "False")

        # Avaliação segura
        try:
            return eval(expr, {"__builtins__": {}})
        except Exception:
            return expr.strip('"').strip("'")

    # =========================
    # CAPTURAR BLOCO
    # =========================
    def _capturar_bloco(self, linhas, start):
        bloco = []
        i = start + 1
        while i < len(linhas) and linhas[i].strip() != "fim":
            bloco.append(linhas[i])
            i += 1
        return bloco

    # =========================
    # PULAR BLOCO
    # =========================
    def _pular_bloco(self, linhas, start):
        i = start + 1
        while i < len(linhas) and linhas[i].strip() != "fim":
            i += 1
        return i + 1

    # =========================
    # CHAMAR FUNÇÃO
    # =========================
    def _chamar_funcao(self, nome, args_str, escopo):
        arg_values = [self._avaliar_expressao(a.strip(), escopo) for a in args_str.split(",") if a.strip()]
        arg_names, bloco = self.funcoes[nome]
        if len(arg_names) != len(arg_values):
            raise LogicStartErro(f"Função '{nome}' recebeu número incorreto de argumentos")
        novo_escopo = dict(zip(arg_names, arg_values))
        self._executar_bloco(bloco, novo_escopo)
