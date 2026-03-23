// editor.js - LogicStart IDE PRO MAX

let editor;
let arquivos = {};
let arquivoAtual = "main.ls";

// ================= INIT =================

window.onload = () => {
    iniciarEditor();
    iniciarUI();
};

// ================= EDITOR =================

function iniciarEditor() {
    editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
        lineNumbers: true,
        mode: "python",
        theme: "material-darker",
        indentUnit: 4,
        tabSize: 4,
        lineWrapping: true,
        extraKeys: {
            "Ctrl-Space": "autocomplete"
        }
    });

    // Autocomplete personalizado
    CodeMirror.registerHelper("hint", "python", function(cm) {
        const cursor = cm.getCursor();
        const token = cm.getTokenAt(cursor);

        const palavras = [
            "variavel", "imprimir", "se", "senao", "fim_se",
            "repetir", "fim_repetir",
            "funcao", "fim_funcao", "retorna"
        ];

        const lista = palavras.filter(p => p.startsWith(token.string));

        return {
            list: lista,
            from: CodeMirror.Pos(cursor.line, token.start),
            to: CodeMirror.Pos(cursor.line, token.end)
        };
    });

    novoArquivo("main.ls");
}

// ================= ARQUIVOS =================

function novoArquivo(nome) {
    arquivos[nome] = "";
    arquivoAtual = nome;
    atualizarAbas();
    editor.setValue("");
}

function salvarArquivo() {
    arquivos[arquivoAtual] = editor.getValue();

    const blob = new Blob([editor.getValue()], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = arquivoAtual;
    a.click();
}

function abrirArquivo(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        arquivoAtual = file.name;
        arquivos[file.name] = e.target.result;
        editor.setValue(e.target.result);
        atualizarAbas();
    };

    reader.readAsText(file);
}

function trocarArquivo(nome) {
    arquivos[arquivoAtual] = editor.getValue();
    arquivoAtual = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

// ================= ABAS =================

function atualizarAbas() {
    const container = document.getElementById("abas");
    container.innerHTML = "";

    Object.keys(arquivos).forEach(nome => {
        const aba = document.createElement("div");
        aba.className = "aba " + (nome === arquivoAtual ? "ativa" : "");
        aba.innerText = nome;

        aba.onclick = () => trocarArquivo(nome);

        container.appendChild(aba);
    });
}

// ================= EXECUÇÃO =================

async function executarCodigo() {
    const codigo = editor.getValue();

    const res = await fetch("/executar", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ codigo })
    });

    const data = await res.json();

    document.getElementById("saida").innerText =
        data.erro ? data.erro : data.saida.join("\n");
}

// ================= UI =================

function iniciarUI() {

    // Botão Run
    document.getElementById("runBtn").onclick = executarCodigo;

    // Botão salvar
    document.getElementById("saveBtn").onclick = salvarArquivo;

    // Input file
    document.getElementById("fileInput").onchange = abrirArquivo;

    // Menu 3 pontinhos
    document.getElementById("menuBtn").onclick = () => {
        const menu = document.getElementById("menu");
        menu.classList.toggle("ativo");
    };
        }
