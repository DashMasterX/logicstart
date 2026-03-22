// ===== CodeMirror =====
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name:"python", version:3, singleLineStringErrors:false},
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
});

// ===== Arquivos simulados =====
let arquivos = {
    "main": "# Seu código LogicStart aqui\n",
    "teste": "// Código de teste\n"
};

function abrirArquivo(nome) {
    editor.setValue(arquivos[nome]);
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    let tab = Array.from(document.querySelectorAll(".tab")).find(t => t.textContent.startsWith(nome));
    if(tab) tab.classList.add("active");
}

function abrirAba(nome) {
    abrirArquivo(nome);
}

// ===== Terminal / saída =====
let terminal = document.getElementById("terminal");
function limparTerminal() { terminal.innerHTML = ""; }

function logTerminal(texto, tipo="info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.textContent = texto;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// ===== Funções dos botões =====
function executarCodigo() {
    let codigo = editor.getValue();
    logTerminal("> Executando...", "info");

    fetch("/run", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            logTerminal(data.result, "success");
        } else {
            logTerminal("Erro: " + data.error, "error");
        }
    })
    .catch(() => logTerminal("Erro de conexão com o servidor", "error"));
}

function salvarCodigo() {
    let codigo = editor.getValue();
    fetch("/save", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success){
            logTerminal("✅ Código salvo com sucesso", "success");
        } else {
            logTerminal("Erro ao salvar: " + data.error, "error");
        }
    })
    .catch(() => logTerminal("Erro de conexão com o servidor", "error"));
}

// Limpar terminal
document.querySelectorAll(".float-buttons button")[2]?.addEventListener("click", limparTerminal);

// Inicializa arquivo principal
abrirArquivo("main");
