# app.py
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
# CONFIGURAÇÃO DO APP
# =========================
app = Flask(__name__)
MAX_CODE_SIZE = 5000

# Logging profissional
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')
logger = logging.getLogger("LogicStart")

# =========================
# MIDDLEWARE: LOG DE REQUISIÇÕES
# =========================
@app.before_request
def log_request():
    logger.info(f"[REQ] {request.method} {request.path}")


# =========================
# ROTAS PRINCIPAIS
# =========================
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        return "LogicStart ONLINE 🚀"


@app.route("/health")
def health():
    return jsonify({"status": "online", "service": "LogicStart", "time": time.time()})


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
        logger.info(f"[EXEC] Tempo de execução: {execution_time}s")

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
# SALVAR CÓDIGO POR EMAIL
# =========================
@app.route("/save_code", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        email = data.get("email")
        codigo = data.get("code")

        if not email or not codigo:
            return jsonify({"success": False, "error": "Email ou código não informado"})

        # Cria pasta para códigos salvos
        pasta = "codigos_salvos"
        os.makedirs(pasta, exist_ok=True)
        # Nome do arquivo seguro
        caminho = os.path.join(pasta, f"{email.replace('@','_at_')}.ls")

        # Salva o código no histórico do usuário
        with open(caminho, "a", encoding="utf-8") as f:
            f.write(codigo + "\n\n---\n\n")

        logger.info(f"[SAVE] Código salvo para {email}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"[SAVE ERROR] {e}")
        return jsonify({"success": False, "error": str(e)})


# =========================
# ERRO PADRÃO
# =========================
def error_response(msg, debug=None):
    return jsonify({"success": False, "error": msg, "debug": debug})


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
# START (CLOUD / LOCAL)
# =========================
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 80))
        logger.info(f"🚀 Iniciando LogicStart na porta {port}")
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Falha ao iniciar: {e}")
