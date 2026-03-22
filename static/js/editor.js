/* ===========================================
   LogicStart Elite Pro Max - editor.js
   Suporte: execução, salvar, múltiplos arquivos,
   terminal estilizado, botões animados.
=========================================== */

/* ===== CodeMirror ===== */
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name:"python", version:3, singleLineStringErrors:false},
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: true,
});

/* ===== Arquivos simulados ===== */
let arquivos = {
    "main": "# Seu código LogicStart aqui\n",
    "teste": "// Código de teste\n"
};
let arquivoAtual = "main";

/* ===== Funções de arquivos ===== */
function abrirArquivo(nome) {
    if (!arquivos[nome]) arquivos[nome] = "";
    editor.setValue(arquivos[nome]);
    arquivoAtual = nome;

    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    let tab = Array.from(document.querySelectorAll(".tab")).find(t => t.textContent.startsWith(nome));
    if (tab) tab.classList.add("active");
}

function abrirAba(nome) {
    salvarArquivoAtual();
    abrirArquivo(nome);
}

function salvarArquivoAtual() {
    arquivos[arquivoAtual] = editor.getValue();
}

/* ===== Terminal / saída ===== */
let terminal = document.getElementById("terminal");

function limparTerminal() { terminal.innerHTML = ""; }

function logTerminal(texto, tipo="info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.textContent = texto;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

/* ===== Executar código via API ===== */
function executarCodigo() {
    salvarArquivoAtual();
    let codigo = editor.getValue();
    logTerminal(`> Executando ${arquivoAtual}...`, "info");

    fetch("/run", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
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
    .catch(() => logTerminal("Erro conexão servidor","error"));
}

/* ===== Salvar código via API ===== */
function salvarCodigo() {
    salvarArquivoAtual();
    let codigo = editor.getValue();
    fetch("/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        logTerminal(data.success ? "Código salvo com sucesso!" : data.error, data.success ? "success" : "error");
    })
    .catch(() => logTerminal("Erro ao salvar no servidor","error"));
}

/* ===== Terminal animado para botões ===== */
function animarBotao(botao) {
    botao.classList.add("active-anim");
    setTimeout(() => botao.classList.remove("active-anim"), 300);
}

/* ===== Botões flutuantes ===== */
document.querySelectorAll(".float-buttons button").forEach(btn => {
    btn.addEventListener("click", () => animarBotao(btn));
});

/* ===== Hotkeys ===== */
document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "Enter") {
        executarCodigo();
        e.preventDefault();
    }
    if (e.ctrlKey && e.key === "s") {
        salvarCodigo();
        e.preventDefault();
    }
});

/* ===== Inicialização ===== */
abrirArquivo(arquivoAtual);
