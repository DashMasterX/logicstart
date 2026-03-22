# gui/screens.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from executor_nodes import ExecutorNodes
from parser import Parser
from errors import LogicStartErro

# Blueprint para separar rotas da IDE
ide_bp = Blueprint("ide", __name__, template_folder="templates")

# Tela do editor
@ide_bp.route("/", methods=["GET", "POST"])
def editor():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        if not codigo:
            flash("⚠️ Nenhum código inserido", "error")
            return redirect(url_for("ide.editor"))

        try:
            # Parse do código para nodes
            parser = Parser(codigo)
            nodes = parser.parse()

            # Executa os nodes
            executor = ExecutorNodes(nodes)
            resultado = executor.executar()

            return render_template("resultado.html", resultado=resultado, codigo=codigo)

        except LogicStartErro as e:
            return render_template("resultado.html", resultado=f"❌ Erro: {e}", codigo=codigo)
        except Exception as e:
            return render_template("resultado.html", resultado=f"❌ Erro inesperado: {e}", codigo=codigo)

    # GET: apenas renderiza o editor vazio
    return render_template("editor.html", codigo="")

# Tela de resultado (pode ser incluída no mesmo template)
@ide_bp.route("/resultado")
def resultado():
    # Apenas exemplo; real usa POST
    return render_template("resultado.html", resultado="Aqui aparecerá o resultado", codigo="")
