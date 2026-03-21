# app.py
from flask import Flask, render_template, request, jsonify, session
import io, sys, time, traceback, logging, os, threading

# -----------------------------
# Configurações Profissionais
# -----------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey123")
MAX_CODE_SIZE = 5000
EXEC_TIMEOUT = 2  # segundos
BLACKLIST = ["import os", "exec(", "eval(", "__import__", "open(", "subprocess"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")

# -----------------------------
# Histórico de execuções
# -----------------------------
EXEC_HISTORY = {}

# -----------------------------
# Funções de segurança
# -----------------------------
def verificar_codigo(codigo: str) -> bool:
    """Bloqueia comandos perigosos"""
    return all(palavra not in codigo for palavra in BLACKLIST)

# -----------------------------
# Execução segura com timeout
# -----------------------------
def executar_codigo(codigo: str, buffer: io.StringIO):
    try:
        exec(codigo, {"__builtins__": {}})
    except Exception as e:
        buffer.write(f"💥 Erro: {e}")

def run_with_timeout(codigo: str, timeout: int = EXEC_TIMEOUT) -> str:
    buffer = io.StringIO()
    thread = threading.Thread(target=executar_codigo, args=(codigo, buffer))
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        return "⏱ Código excedeu o tempo limite"
    return buffer.getvalue() or "✔ Executado com sucesso"

# -----------------------------
# Rotas principais
# -----------------------------
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        return "LogicStart IDE Online 🚀"

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

        if len(codigo) > MAX_CODE_SIZE:
            return error_response("Código muito grande")
        if not verificar_codigo(codigo):
            return error_response("Código bloqueado por segurança")

        output = run_with_timeout(codigo)
        execution_time = round(time.time() - start_time, 4)
        logger.info(f"[EXEC] Tempo: {execution_time}s | Saída: {output[:50]}")

        # Identifica usuário único (IP + session)
        user_id = session.get("user_id", request.remote_addr)
        if user_id not in EXEC_HISTORY:
            EXEC_HISTORY[user_id] = []
        EXEC_HISTORY[user_id].append({
            "code": codigo,
            "result": output,
            "time": execution_time,
            "timestamp": time.time()
        })
        # Mantém apenas últimas 20 execuções
        EXEC_HISTORY[user_id] = EXEC_HISTORY[user_id][-20:]

        return jsonify({"success": True, "result": output, "time": execution_time})

    except Exception:
        erro = traceback.format_exc()
        logger.error(f"[CRASH]\n{erro}")
        return error_response("Erro interno", debug=erro)

@app.route("/history")
def history():
    user_id = session.get("user_id", request.remote_addr)
    return jsonify({"history": EXEC_HISTORY.get(user_id, [])})

# -----------------------------
# Função de erro
# -----------------------------
def error_response(msg, debug=None):
    return jsonify({"success": False, "error": msg, "debug": debug})

# -----------------------------
# Handlers globais
# -----------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Erro interno do servidor"}), 500

# -----------------------------
# Start do servidor (Cloud Ready)
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    logger.info(f"🚀 LogicStart iniciando na porta {port}")
    app.run(host="0.0.0.0", port=port, threaded=True)
