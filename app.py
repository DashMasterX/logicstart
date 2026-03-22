# app.py | LogicStart Elite Web - Nível Empresa Apple Pro Max

from flask import Flask, render_template, request, jsonify
from executor_nodes import ExecutorNodes
from nodes import Mostrar, Guardar, Repetir, Condicao, Funcao, Retorna
from security import Security
from errors import LogicStartErro

# =============================
# App Flask
# =============================
app = Flask(__name__)

# =============================
# Página inicial / login
# =============================
@app.route("/", methods=["GET"])
def index():
    return render_template("login.html")  # HTML separado no templates/login.html

@app.route("/editor", methods=["GET"])
def editor():
    return render_template("editor.html")  # Editor web

# =============================
# Executar código
# =============================
@app.route("/executar", methods=["POST"])
def executar():
    codigo = request.json.get("codigo", "").strip()
    if not codigo:
        return jsonify({"status": "erro", "saida": "⚠ Nenhum código inserido"})

    try:
        # Segurança
        Security().verificar(codigo)

        # Aqui você faria o parse real, mas para teste:
        nodes = [
            Mostrar("Olá mundo!"),
            Guardar("x", "10"),
            Mostrar("x")
        ]

        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        return jsonify({"status": "ok", "saida": resultado})

    except LogicStartErro as e:
        return jsonify({"status": "erro", "saida": f"Erro: {e}"})
    except Exception as e:
        return jsonify({"status": "erro", "saida": f"Erro inesperado: {e}"})

# =============================
# Rodar app
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
