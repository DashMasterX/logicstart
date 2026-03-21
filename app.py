from flask import Flask, request, jsonify, render_template, session, redirect
import os, io, sys, time, logging
from engine import LogicStart
from security import Security

app = Flask(__name__)
app.secret_key = os.urandom(24)
MAX_CODE_SIZE = 5000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogicStart")

# ---------------------------
# ROTAS PÚBLICAS
# ---------------------------
@app.route("/")
def index(): return render_template("index.html")
@app.route("/login") 
def login(): return render_template("login.html")

@app.route("/login/email", methods=["POST"])
def login_email():
    data = request.get_json()
    email, senha = data.get("email"), data.get("senha")
    if email and senha: 
        session["user"] = {"email": email}
        return jsonify({"success": True})
    return jsonify({"success": False, "error":"Email ou senha inválidos"})

@app.route("/login/google")
def login_google():
    session["user"] = {"email":"usuario@gmail.com"}
    return redirect("/ide")

@app.route("/ide")
def ide():
    if "user" not in session: return redirect("/login")
    return render_template("ide.html")

# ---------------------------
# EXECUÇÃO DE CÓDIGO
# ---------------------------
@app.route("/run", methods=["POST"])
def run_code():
    if "user" not in session: return jsonify({"success": False, "error":"Faça login primeiro"})
    start = time.time()
    data = request.get_json()
    codigo = data.get("code")
    if not codigo: return jsonify({"success": False, "error":"Código não enviado"})
    if len(codigo) > MAX_CODE_SIZE: return jsonify({"success": False, "error":"Código muito grande"})
    if not Security().verificar(codigo): return jsonify({"success": False, "error":"Código bloqueado"})

    buffer = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        logic = LogicStart(codigo)
        logic.executar()
        output = buffer.getvalue()
    finally: sys.stdout = old_stdout
    return jsonify({"success": True, "result": output if output else "✔ Executado", "time": round(time.time()-start,4)})

# ---------------------------
# SALVAR CÓDIGO
# ---------------------------
@app.route("/save", methods=["POST"])
def save_code():
    if "user" not in session: return jsonify({"success": False, "error":"Faça login primeiro"})
    data = request.get_json()
    codigo, email = data.get("code"), data.get("email")
    if not codigo or not email: return jsonify({"success": False, "error":"Código ou e-mail não enviado"})
    user_dir = os.path.join("history", email.replace("@","_"))
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"codigo_{int(time.time())}.txt")
    with open(file_path,"w",encoding="utf-8") as f: f.write(codigo)
    return jsonify({"success": True, "message":"Código salvo com sucesso!"})

# ---------------------------
# ERROS
# ---------------------------
@app.errorhandler(404)
def not_found(e): return jsonify({"error":"Rota não encontrada"}),404
@app.errorhandler(500)
def internal_error(e): return jsonify({"error":"Erro interno do servidor"}),500

# ---------------------------
# START
# ---------------------------
if __name__=="__main__":
    os.makedirs("history", exist_ok=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",80)))
