from flask import Flask, render_template, request, jsonify
from engine import LogicStart
from errors import LogicStartErro
from security import Security

import io
import sys
import traceback
import time

app = Flask(__name__)

# =========================
# CONFIG
# =========================
MAX_CODE_SIZE = 5000  # limite de segurança


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/run", methods=["POST"])
def run_code():
    start_time = time.time()

    try:
        data = request.get_json()

        if not data or "code" not in data:
            return error_response("Código não enviado")

        codigo = data["code"]

        # =========================
        # SEGURANÇA
        # =========================
        if len(codigo) > MAX_CODE_SIZE:
            return error_response("Código muito grande")

        if not Security().verificar(codigo):
            return error_response("Código bloqueado por segurança")

        # =========================
        # EXECUÇÃO ISOLADA
        # =========================
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            logic = LogicStart(codigo)
            logic.executar()

            output = buffer.getvalue()

        finally:
            sys.stdout = old_stdout

        # =========================
        # RESPOSTA
        # =========================
        execution_time = round(time.time() - start_time, 4)

        return jsonify({
            "success": True,
            "result": output if output else "✔ Executado com sucesso",
            "time": execution_time
        })

    except LogicStartErro as e:
        return error_response(str(e))

    except Exception:
        erro = traceback.format_exc()
        return error_response("Erro interno", debug=erro)


# =========================
# FUNÇÕES AUXILIARES
# =========================
def error_response(msg, debug=None):
    return jsonify({
        "success": False,
        "error": msg,
        "debug": debug
    })


# =========================
# START
# =========================
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
