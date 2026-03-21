import ast
import operator

# =========================
# EXCEÇÕES
# =========================
class LogicStartErro(Exception):
    pass

# =========================
# EXECUTOR
# =========================
class LogicStart:
    def __init__(self, codigo: str):
        self.codigo = codigo
        self.vars = {}      # Armazena variáveis
        self.consts = {}    # Armazena constantes
        self.functions = {} # Armazena funções
        self.classes = {}   # Armazena classes

    # =========================
    # EXECUTAR
    # =========================
    def executar(self):
        linhas = [l.strip() for l in self.codigo.split('\n') if l.strip()]
        for i, linha in enumerate(linhas, 1):
            try:
                self._executar_linha(linha)
            except Exception as e:
                raise LogicStartErro(f"Linha {i}: {e}")

    # =========================
    # PARSER SIMPLIFICADO
    # =========================
    def _executar_linha(self, linha):
        # Comentário
        if linha.startswith("//"):
            return

        # Variável
        if linha.startswith("variavel "):
            nome, valor = self._parse_assign(linha[8:])
            self.vars[nome] = valor
            return

        # Constante
        if linha.startswith("constante "):
            nome, valor = self._parse_assign(linha[10:])
            self.consts[nome] = valor
            return

        # Impressão
        if linha.startswith("imprima(") and linha.endswith(")"):
            conteudo = linha[8:-1]
            print(self._avaliar_expressao(conteudo))
            return

        # Retorno
        if linha.startswith("retorne "):
            valor = self._avaliar_expressao(linha[7:])
            raise LogicStartErro(f"retorne usado fora de função: {valor}")

        # TODO: Funções, classes, loops, condicionais
        # Para simplificação inicial, apenas variáveis, constantes e impressão
        raise LogicStartErro(f"Comando desconhecido: {linha}")

    # =========================
    # ASSIGNMENT PARSER
    # =========================
    def _parse_assign(self, texto):
        if "=" not in texto:
            raise LogicStartErro("Atribuição inválida")
        partes = texto.split("=",1)
        nome = partes[0].strip()
        valor = self._avaliar_expressao(partes[1].strip())
        return nome, valor

    # =========================
    # AVALIAR EXPRESSÃO
    # =========================
    def _avaliar_expressao(self, expr):
        # Substitui variáveis e constantes
        for nome, valor in {**self.vars, **self.consts}.items():
            expr = expr.replace(nome, str(valor))
        try:
            return eval(expr, {"__builtins__": {}}, {})
        except Exception:
            return expr  # Retorna string literal se não for número/expressão
