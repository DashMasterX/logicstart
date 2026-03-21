# engine.py
from security import Security, MAX_LOOP
from errors import LogicStartErro
import re

class LogicStart:
    """
    Interpretador LogicStart Profissional (Português estilo JavaScript)
    """

    def __init__(self, codigo):
        self.codigo = codigo
        self.variaveis = {}
        self.funcoes = {}
        self.security = Security()

        # Verifica segurança
        if not self.security.verificar(codigo):
            raise LogicStartErro("Código bloqueado por segurança")

    def executar(self):
        self._executar_bloco(self.codigo.splitlines(), self.variaveis)

    # =========================
    # EXECUTA BLOCO
    # =========================
    def _executar_bloco(self, linhas, escopo):
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if not linha or linha.startswith("//"):
                i += 1
                continue

            # Variável
            match_var = re.match(r"variavel\s+(\w+)\s*=\s*(.+)", linha)
            if match_var:
                nome, valor = match_var.groups()
                escopo[nome] = self._avaliar(valor, escopo)
                i += 1
                continue

            # Função
            match_func = re.match(r"funcao\s+(\w+)\((.*)\):", linha)
            if match_func:
                nome, args = match_func.groups()
                bloco = self._capturar_bloco(linhas, i)
                self.funcoes[nome] = (args.split(",") if args.strip() else [], bloco)
                i += len(bloco) + 2
                continue

            # Chamada de função
            match_call = re.match(r"(\w+)\((.*)\)", linha)
            if match_call and match_call.group(1) in self.funcoes:
                self._chamar_funcao(match_call.group(1), match_call.group(2), escopo)
                i += 1
                continue

            # Mostrar
            match_mostrar = re.match(r"mostrar\s+(.+)", linha)
            if match_mostrar:
                print(self._avaliar(match_mostrar.group(1), escopo))
                i += 1
                continue

            # Condicional
            if linha.startswith("se "):
                cond = re.match(r"se\s+(.+):", linha).group(1)
                if self._avaliar(cond, escopo):
                    i += 1
                else:
                    i = self._pular_bloco(linhas, i)
                continue

            if linha.startswith("senao:"):
                i += 1
                continue

            # Loop repetir
            match_repetir = re.match(r"repetir\s+(\d+)\s+vezes:", linha)
            if match_repetir:
                vezes = int(match_repetir.group(1))
                bloco = self._capturar_bloco(linhas, i)
                for _ in range(vezes):
                    self._executar_bloco(bloco, dict(escopo))
                i += len(bloco) + 2
                continue

            # Loop enquanto
            match_enquanto = re.match(r"enquanto\s+(.+):", linha)
            if match_enquanto:
                cond = match_enquanto.group(1)
                bloco = self._capturar_bloco(linhas, i)
                loop_count = 0
                while self._avaliar(cond, escopo):
                    if loop_count > MAX_LOOP:
                        raise LogicStartErro("Loop infinito detectado")
                    self._executar_bloco(bloco, dict(escopo))
                    loop_count += 1
                i += len(bloco) + 2
                continue

            # Fim de bloco
            if linha == "fim":
                i += 1
                continue

            raise LogicStartErro(f"Comando desconhecido: {linha}")

    # =========================
    # AVALIA EXPRESSÃO
    # =========================
    def _avaliar(self, expr, escopo):
        for nome, valor in escopo.items():
            valor_str = f'"{valor}"' if isinstance(valor, str) else str(valor)
            expr = re.sub(rf"\b{nome}\b", valor_str, expr)
        expr = expr.replace("verdadeiro", "True").replace("falso", "False")
        try:
            return eval(expr, {"__builtins__": {}})
        except Exception:
            return expr.strip('"').strip("'")

    # =========================
    # CAPTURA BLOCO
    # =========================
    def _capturar_bloco(self, linhas, start):
        bloco = []
        i = start + 1
        while i < len(linhas) and linhas[i].strip() != "fim":
            bloco.append(linhas[i])
            i += 1
        return bloco

    # =========================
    # PULA BLOCO
    # =========================
    def _pular_bloco(self, linhas, start):
        i = start + 1
        while i < len(linhas) and linhas[i].strip() != "fim":
            i += 1
        return i + 1

    # =========================
    # CHAMA FUNÇÃO
    # =========================
    def _chamar_funcao(self, nome, args_str, escopo):
        arg_values = [self._avaliar(a.strip(), escopo) for a in args_str.split(",") if a.strip()]
        arg_names, bloco = self.funcoes[nome]
        if len(arg_names) != len(arg_values):
            raise LogicStartErro(f"Função '{nome}' recebeu número incorreto de argumentos")
        novo_escopo = dict(zip(arg_names, arg_values))
        self._executar_bloco(bloco, novo_escopo)
