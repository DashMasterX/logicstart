# parser_complexo.py - Parser nível empresa LogicStart Elite
import re
from nodes import Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao, Funcao, Retorna, ChamadaFuncao

class ParserError(Exception):
    def __init__(self, msg, linha=None):
        self.linha = linha
        self.msg = f"Linha {linha}: {msg}" if linha else msg
        super().__init__(self.msg)

def parse_codigo(codigo):
    """
    Parser complexo que converte código LogicStart em nodes executáveis.
    """
    nodes = []
    pilha_indent = [(0, nodes)]
    linhas = codigo.splitlines()

    for i, linha in enumerate(linhas, start=1):
        original = linha
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue  # Ignora comentários e linhas vazias

        indent = len(original) - len(original.lstrip())
        while pilha_indent and indent < pilha_indent[-1][0]:
            pilha_indent.pop()
        if not pilha_indent:
            raise ParserError("Indentação incorreta", i)

        contexto = pilha_indent[-1][1]

        # ===== Variável =====
        m_var = re.match(r"variavel\s+(\w+)\s*=\s*(.+)", linha, re.I)
        if m_var:
            nome, valor = m_var.groups()
            contexto.append(Guardar(nome, valor))
            continue

        # ===== Imprimir =====
        m_print = re.match(r"imprimir\((.*)\)", linha, re.I)
        if m_print:
            contexto.append(Mostrar(m_print.group(1)))
            continue

        # ===== Repetir =====
        m_repetir = re.match(r"repetir\s+(\d+):", linha, re.I)
        if m_repetir:
            vezes = int(m_repetir.group(1))
            bloco = []
            contexto.append(Repetir(vezes, bloco))
            pilha_indent.append((indent + 4, bloco))
            continue

        # ===== Enquanto =====
        m_enquanto = re.match(r"enquanto\s+(.+):", linha, re.I)
        if m_enquanto:
            condicao = m_enquanto.group(1)
            bloco = []
            contexto.append(Enquanto(condicao, bloco))
            pilha_indent.append((indent + 4, bloco))
            continue

        # ===== Se =====
        m_se = re.match(r"se\s+(.+):", linha, re.I)
        if m_se:
            cond = m_se.group(1)
            bloco = []
            contexto.append(Condicao(cond, bloco))
            pilha_indent.append((indent + 4, bloco))
            continue

        # ===== SeSenao =====
        m_senao = re.match(r"senao:", linha, re.I)
        if m_senao:
            if not contexto or not isinstance(contexto[-1], Condicao):
                raise ParserError("senao sem se correspondente", i)
            bloco_false = []
            cond_node = contexto[-1]
            contexto.pop()
            cond_senao_node = SeSenao(cond_node.condicao, cond_node.bloco, bloco_false)
            pilha_indent[-1][1].append(cond_senao_node)
            pilha_indent.append((indent + 4, bloco_false))
            continue

        # ===== Função =====
        m_func = re.match(r"funcao\s+(\w+)\((.*?)\):", linha, re.I)
        if m_func:
            nome, params = m_func.groups()
            params = [p.strip() for p in params.split(",") if p.strip()]
            bloco = []
            contexto.append(Funcao(nome, params, bloco))
            pilha_indent.append((indent + 4, bloco))
            continue

        # ===== Retorna =====
        m_retorna = re.match(r"retorna\s+(.+)", linha, re.I)
        if m_retorna:
            contexto.append(Retorna(m_retorna.group(1)))
            continue

        # ===== Chamada de função =====
        m_chamada = re.match(r"(\w+)\((.*?)\)", linha)
        if m_chamada:
            nome, args = m_chamada.groups()
            args = [a.strip() for a in args.split(",") if a.strip()]
            contexto.append(ChamadaFuncao(nome, args))
            continue

        # ===== Erro =====
        raise ParserError(f"Comando não reconhecido: {linha}", i)

    return nodes
