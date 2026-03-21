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
from functools import wraps

# =========================
# CONFIGURAÇÃO APP
# =========================
app = Flask(__name__)
MAX_CODE_SIZE = 5000  # Limite de caracteres

# =========================
# LOGGING PROFISSIONAL
# =========================
logger = logging.getLogger("LogicStart")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# =========================
# MIDDLEWARE
# =========================
@app.before_request
def log_request():
    logger.info(f"[REQ] {request.method} {request.path} from {request.remote_addr}")

def execution_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        response = func(*args, **kwargs)
        exec_time = round(time.time() - start_time, 4)
        logger.info(f"[EXEC TIME] {request.path} -> {exec_time}s")
        return response
    return wrapper

# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Falha ao renderizar index.html: {e}")
        return "LogicStart ONLINE 🚀"

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "service": "LogicStart",
        "time": time.time()
    })

@app.route("/run", methods=["POST"])
@execution_timer
def run_code():
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
        finally:
            sys.stdout = old_stdout

        output = buffer.getvalue() or "✔ Executado com sucesso"
        return jsonify({
            "success": True,
            "result": output
        })

    except LogicStartErro as e:
        logger.warning(f"[LOGIC ERROR] {e}")
        return error_response(str(e))
    except Exception:
        erro = traceback.format_exc()
        logger.error(f"[CRASH] {erro}")
        return error_response("Erro interno", debug=erro)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def error_response(msg, debug=None):
    return jsonify({
        "success": False,
        "error": msg,
        "debug": debug
    }), 400

# =========================
# HANDLERS GLOBAIS
# =========================
@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404: {request.path}")
    return jsonify({"success": False, "error": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.critical(f"500: {request.path} - {e}")
    return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

# =========================
# START CLOUD/LOCAL
# =========================
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 80))
        logger.info(f"🚀 Iniciando LogicStart na porta {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Falha ao iniciar: {e}")
