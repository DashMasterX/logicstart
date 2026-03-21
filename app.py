from flask import Flask, render_template, request, jsonify
from engine import LogicStart
from security import Security
from errors import LogicStartErro

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
logger = logging.getLogger("LogicStartIDE")

# Segurança e limites
MAX_CODE_SIZE = 5000

# Lista de comandos da linguagem LogicStart (em português)
COMMANDS = [
    "se", "senao", "enquanto", "para", "funcao", "retorne",
    "imprima", "constante", "variavel", "classe", "novo"
]

# Armazenamento simples de códigos salvos (em memória, para exemplo)
SAVED_CODES = {}  # {email: [lista de códigos]}


# =========================
# ROTAS
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({"status": "online", "service": "LogicStartIDE", "time": time.time()})


@app.route("/run", methods=["POST"])
def run_code():
    start_time = time.time()
    try:
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"success": False, "error": "Código não enviado"})

        codigo = data["code"]

        # =========================
        # SEGURANÇA
        # =========================
        if len(codigo) > MAX_CODE_SIZE:
            return jsonify({"success": False, "error": "Código muito grande"})

        if not Security().verificar(codigo):
            return jsonify({"success": False, "error": "Código bloqueado por segurança"})

        # =========================
        # EXECUÇÃO
        # =========================
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            logic = LogicStart(codigo)
            logic.executar()
            output = buffer.getvalue() or "✔ Executado com sucesso"

        finally:
            sys.stdout = old_stdout

        execution_time = round(time.time() - start_time, 4)
        return jsonify({"success": True, "result": output, "time": execution_time})

    except LogicStartErro as e:
        return jsonify({"success": False, "error": str(e)})

    except Exception:
        erro = traceback.format_exc()
        return jsonify({"success": False, "error": "Erro interno", "debug": erro})


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
            return jsonify({"success": False, "error": "Email ou código não fornecido"})

        if email not in SAVED_CODES:
            SAVED_CODES[email] = []
        SAVED_CODES[email].append(codigo)

        logger.info(f"Código salvo para {email}")
        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# =========================
# AUTOCOMPLETE
# =========================
@app.route("/autocomplete")
def autocomplete():
    prefixo = request.args.get("prefixo","").lower()
    sugeridos = [c for c in COMMANDS if c.startswith(prefixo)]
    return jsonify({"suggestions": sugeridos})


# =========================
# ERRO PADRÃO
# =========================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Erro interno do servidor"}), 500


# =========================
# START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    logger.info(f"🚀 LogicStartIDE iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port)
