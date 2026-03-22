# app.py - LogicStart Elite Web Profissional
from flask import Flask, render_template, request, redirect, url_for, jsonify
from executor_nodes import ExecutorNodes
from nodes import (
    Mostrar, Guardar, Repetir, Enquanto, Condicao, SeSenao,
    Funcao, Retorna, ChamadaFuncao, BreakLoop, ContinueLoop
)

app = Flask(__name__)

# -------------------------
# Sessão simples
# -------------------------
SESSAO = {"logado": False}

# -------------------------
# Rotas de login
# -------------------------
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email = data.get("email", "").strip()
    senha = data.get("senha", "").strip()
    if (email == "admin" and senha == "1234") or (email == "" and senha == ""):
        SESSAO["logado"] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Usuário ou senha inválidos"})

@app.route("/login/guest")
def login_guest():
    SESSAO["logado"] = True
    return redirect(url_for("ide"))

# -------------------------
# IDE
# -------------------------
@app.route("/ide", methods=["GET"])
def ide():
    if not SESSAO.get("logado"):
        return redirect(url_for("login_page"))
    return render_template("ide.html", resultado="", codigo="", error="")

# -------------------------
# Endpoint para rodar código
# -------------------------
@app.route("/run", methods=["POST"])
def run_code():
    if not SESSAO.get("logado"):
        return jsonify({"success": False, "error": "Não logado"})

    data = request.get_json()
    codigo = data.get("code", "").strip()

    if not codigo:
        return jsonify({"success": False, "error": "⚠ Nenhum código inserido"})

    try:
        # =========================
        # Parser básico para nodes reais
        # =========================
        nodes = parse_codigo(codigo)

        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        return jsonify({"success": True, "result": resultado})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# -------------------------
# Logout
# -------------------------
@app.route("/logout")
def logout():
    SESSAO["logado"] = False
    return redirect(url_for("login_page"))

# -------------------------
# Rodar app na Square Cloud na porta 80
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

# =========================
# Função de parser avançado
# =========================
def parse_codigo(codigo_texto):
    """
    Converte código estilo LogicStart em Nodes reais para execução.
    Suporta:
        - variavel x = 10
        - imprimir(x)
        - repetir 5:
        - enquanto x < 10:
        - se x == 10:
        - senão:
        - funções
        - return
    """
    nodes = []
    pilha_blocos = [nodes]
    linhas = codigo_texto.splitlines()
    indentacoes = [0]

    for linha in linhas:
        linha_bruta = linha
        linha = linha.rstrip()
        if not linha or linha.startswith("#"):
            continue

        # Detecta indentação
        indent = len(linha) - len(linha.lstrip())
        while indent < indentacoes[-1]:
            pilha_blocos.pop()
            indentacoes.pop()

        bloco_atual = pilha_blocos[-1]
        linha = linha.strip()

        # ------------------------
        # Variável
        if linha.startswith("variavel "):
            partes = linha[len("variavel "):].split("=", 1)
            nome = partes[0].strip()
            valor = partes[1].strip()
            bloco_atual.append(Guardar(nome, valor))
            continue

        # ------------------------
        # Mostrar
        if linha.startswith("imprimir(") and linha.endswith(")"):
            valor = linha[len("imprimir("):-1].strip()
            bloco_atual.append(Mostrar(valor))
            continue

        # ------------------------
        # Repetir
        if linha.startswith("repetir ") and linha.endswith(":"):
            vezes = int(linha[len("repetir "):-1].strip())
            novo_bloco = []
            bloco_atual.append(Repetir(vezes, novo_bloco))
            pilha_blocos.append(novo_bloco)
            indentacoes.append(indent + 4)
            continue

        # ------------------------
        # Enquanto
        if linha.startswith("enquanto ") and linha.endswith(":"):
            cond = linha[len("enquanto "):-1].strip()
            novo_bloco = []
            bloco_atual.append(Enquanto(cond, novo_bloco))
            pilha_blocos.append(novo_bloco)
            indentacoes.append(indent + 4)
            continue

        # ------------------------
        # Se / Senão
        if linha.startswith("se ") and linha.endswith(":"):
            cond = linha[len("se "):-1].strip()
            novo_bloco = []
            bloco_atual.append(SeSenao(cond, novo_bloco, []))
            pilha_blocos.append(novo_bloco)
            indentacoes.append(indent + 4)
            continue

        if linha.startswith("senao:"):
            if isinstance(bloco_atual[-1], SeSenao):
                # Mover bloco falso
                novo_bloco = []
                bloco_atual[-1].bloco_false = novo_bloco
                pilha_blocos.append(novo_bloco)
                indentacoes.append(indent + 4)
            continue

        # ------------------------
        # Retorna
        if linha.startswith("retorna"):
            valor = linha[len("retorna"):].strip()
            bloco_atual.append(Retorna(valor))
            continue

        # ------------------------
        # Função
        if linha.startswith("funcao ") and linha.endswith(":"):
            nome = linha[len("funcao "):-1].strip()
            novo_bloco = []
            bloco_atual.append(Funcao(nome, [], novo_bloco))
            pilha_blocos.append(novo_bloco)
            indentacoes.append(indent + 4)
            continue

        # ------------------------
        # Chamadas de função
        if "(" in linha and linha.endswith(")"):
            nome = linha.split("(")[0].strip()
            params = linha.split("(")[1][:-1].split(",")
            params = [p.strip() for p in params if p.strip()]
            bloco_atual.append(ChamadaFuncao(nome, params))
            continue

        # ------------------------
        # Expressão não identificada
        bloco_atual.append(Mostrar(linha))

    return nodes
