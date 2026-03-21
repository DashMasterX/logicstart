from flask import Flask, render_template, request, jsonify
from engine import LogicStart
from errors import LogicStartErro
from security import Security

import io
import sys
import traceback
import time
import os
import logging

# =========================
# CONFIG APP
# =========================
app = Flask(__name__)

# Logging profissional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")

# Segurança
MAX_CODE_SIZE = 5000


# =========================
# MIDDLEWARE (LOG REQUEST)
# =========================
@app.before_request
def log_request():
    logger.info(f"[REQ] {request.method} {request.path}")


# =========================
# ROTAS
# =========================

@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        return "LogicStart ONLINE 🚀"


@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "service": "LogicStart",
        "time": time.time()
    })


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
        # EXECUÇÃO SEGURA
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

        execution_time = round(time.time() - start_time, 4)

        logger.info(f"[EXEC] Tempo: {execution_time}s")

        return jsonify({
            "success": True,
            "result": output if output else "✔ Executado com sucesso",
            "time": execution_time
        })

    except LogicStartErro as e:
        logger.warning(f"[LOGIC ERROR] {e}")
        return error_response(str(e))

    except Exception:
        erro = traceback.format_exc()
        logger.error(f"[CRASH]\n{erro}")
        return error_response("Erro interno", debug=erro)


# =========================
# ERRO PADRÃO
# =========================
def error_response(msg, debug=None):
    return jsonify({
        "success": False,
        "error": msg,
        "debug": debug
    })


# =========================
# HANDLER GLOBAL
# =========================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada"}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Erro interno do servidor"}), 500


# =========================
# START (COMPATÍVEL CLOUD)
# =========================
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 80))
        logger.info(f"🚀 Iniciando LogicStart na porta {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Falha ao iniciar: {e}")
