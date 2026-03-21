from flask import Flask, request, jsonify, render_template
from engine import LogicStart
import io, sys, os, time, logging
from security import Security

# =========================
# CONFIGURAÇÃO APP
# =========================
app = Flask(__name__)

# Logging profissional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")

# Limite de tamanho do código
MAX_CODE_SIZE = 5000

# =========================
# MIDDLEWARE - LOG DE REQUISIÇÕES
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
        return "LogicStart IDE ONLINE 🚀"

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

        execution_time = round(time.time() - start_time, 4)
        logger.info(f"[EXEC] Tempo: {execution_time}s")

        return jsonify({
            "success": True,
            "result": output if output else "✔ Executado com sucesso",
            "time": execution_time
        })

    except Exception as e:
        erro = str(e)
        logger.error(f"[CRASH] {erro}")
        return error_response("Erro interno", debug=erro)

@app.route("/save", methods=["POST"])
def save_code():
    try:
        data = request.get_json()
        if not data or "code" not in data or "email" not in data:
            return error_response("Código ou e-mail não enviado")

        codigo = data["code"]
        email = data["email"]

        # Validar código e e-mail
        if len(codigo) > MAX_CODE_SIZE:
            return error_response("Código muito grande")
        if "@" not in email:
            return error_response("E-mail inválido")

        # Salvar código (simples arquivo por usuário)
        user_dir = os.path.join("history", email.replace("@","_"))
        os.makedirs(user_dir, exist_ok=True)
        timestamp = int(time.time())
        file_path = os.path.join(user_dir, f"codigo_{timestamp}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(codigo)

        logger.info(f"[SAVE] Código salvo para {email}")
        return jsonify({"success": True, "message": "Código salvo com sucesso!"})

    except Exception as e:
        logger.error(f"[SAVE ERROR] {str(e)}")
        return error_response("Falha ao salvar código", debug=str(e))

# =========================
# FUNÇÕES AUXILIARES
# =========================
def error_response(msg, debug=None):
    return jsonify({
        "success": False,
        "error": msg,
        "debug": debug
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Rota não encontrada"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Erro interno do servidor"}), 500

# =========================
# START APP
# =========================
if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT", 80))
        logger.info(f"🚀 LogicStart IDE iniciando na porta {port}")
        os.makedirs("history", exist_ok=True)
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        logger.critical(f"Falha ao iniciar: {e}")
