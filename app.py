from flask import Flask, render_template, request, jsonify
from engine import LogicStart
from errors import LogicStartErro
from security import Security

import io, sys, traceback, time, os, logging

app = Flask(__name__, static_folder="static", template_folder="templates")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")
MAX_CODE_SIZE = 5000

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    start_time = time.time()
    try:
        data = request.get_json()
        if not data or "code" not in data:
            return jsonify({"success": False, "error": "Código não enviado"})

        codigo = data["code"]

        if len(codigo) > MAX_CODE_SIZE:
            return jsonify({"success": False, "error": "Código muito grande"})
        if not Security().verificar(codigo):
            return jsonify({"success": False, "error": "Código bloqueado por segurança"})

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
        return jsonify({"success": False, "error": str(e)})
    except Exception:
        erro = traceback.format_exc()
        logger.error(f"[CRASH]\n{erro}")
        return jsonify({"success": False, "error": "Erro interno", "debug": erro})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 80))
    logger.info(f"🚀 Iniciando LogicStart na porta {port}")
    app.run(host="0.0.0.0", port=port)
