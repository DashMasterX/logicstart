from flask import Flask, request, jsonify, render_template
import io
import sys
import os
import time
import logging

# =========================
# CONFIGURAÇÃO
# =========================
app = Flask(__name__)
MAX_CODE_SIZE = 5000  # limite de código
CODE_SAVE_FOLDER = "codes"  # pasta para salvar códigos

# Logging profissional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")

# Cria pasta de códigos caso não exista
os.makedirs(CODE_SAVE_FOLDER, exist_ok=True)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def error_response(msg, debug=None):
    return jsonify({"success": False, "error": msg, "debug": debug})

def save_code(email, code):
    filename = os.path.join(CODE_SAVE_FOLDER, f"{email}_{int(time.time())}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename

# =========================
# ROTAS
# =========================
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
        
        code = data["code"]

        # Segurança
        if len(code) > MAX_CODE_SIZE:
            return error_response("Código muito grande")
        
        # Executa código em sandbox simples
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer

        try:
            # Executa código com globals limitados
            exec(code, {"__builtins__": {}})
        finally:
            sys.stdout = old_stdout

        execution_time = round(time.time() - start_time, 4)
        output = buffer.getvalue()
        logger.info(f"[EXEC] Tempo: {execution_time}s")

        return jsonify({"success": True, "result": output if output else "✔ Executado com sucesso", "time": execution_time})
    
    except Exception as e:
        logger.error(f"[CRASH] {e}")
        return error_response("Erro interno", debug=str(e))

@app.route("/save", methods=["POST"])
def save():
    try:
        data = request.get_json()
        if not data or "email" not in data or "code" not in data:
            return error_response("Email ou código não enviados")

        email = data["email"]
        code = data["code"]
        filepath = save_code(email, code)
        logger.info(f"[SAVE] Código salvo: {filepath}")
        return jsonify({"success": True, "message": f"Código salvo com sucesso em {filepath}"})
    
    except Exception as e:
        logger.error(f"[SAVE ERROR] {e}")
        return error_response("Erro ao salvar código", debug=str(e))

# =========================
# HANDLER DE ERROS
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
    logger.info(f"🚀 Iniciando LogicStart na porta {port}")
    app.run(host="0.0.0.0", port=port)
