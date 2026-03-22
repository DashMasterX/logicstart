# app.py | LogicStart Elite Web - Nível Empresa Apple Pro Max

from flask import Flask, render_template, request, jsonify
from parser import Parser
from executor_nodes import ExecutorNodes
from security import Security
from errors import LogicStartErro

app = Flask(__name__)

# =============================
# Página Inicial / Editor
# =============================
@app.route("/")
def index():
    return render_template("index.html")

# =============================
# Executar Código
# =============================
@app.route("/executar", methods=["POST"])
def executar():
    codigo = request.json.get("codigo", "")
    
    if not codigo.strip():
        return jsonify({"status": "error", "saida": "⚠ Nenhum código inserido"})
    
    try:
        # Verificar segurança
        Security().verificar(codigo)

        # Transformar em nodes via parser
        parser = Parser(codigo)
        nodes = parser.parse()

        # Executar nodes
        executor = ExecutorNodes(nodes)
        resultado = executor.executar()
        
        return jsonify({"status": "ok", "saida": resultado})
    
    except LogicStartErro as e:
        return jsonify({"status": "error", "saida": f"Erro de lógica: {e}"})
    except Exception as e:
        return jsonify({"status": "error", "saida": f"Erro inesperado: {e}"})

# =============================
# Rodar Servidor
# =============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
