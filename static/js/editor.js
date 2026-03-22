// =======================
// CodeMirror Editor Setup
// =======================
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: { name: "python", version: 3, singleLineStringErrors: false },
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: true,
    scrollbarStyle: "simple",
    extraKeys: {
        "Ctrl-S": () => salvarCodigo(),
        "Ctrl-Enter": () => executarCodigo()
    }
});

// =======================
// Arquivos Simulados
// =======================
let arquivos = {
    "main": "# Código principal LogicStart\n",
    "teste": "// Código de teste\n"
};
let arquivoAtual = "main";

function abrirArquivo(nome) {
    arquivoAtual = nome;
    editor.setValue(arquivos[nome]);
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    let tab = Array.from(document.querySelectorAll(".tab")).find(t => t.textContent.startsWith(nome));
    if (tab) tab.classList.add("active");
}

function abrirAba(nome) { abrirArquivo(nome); }

// =======================
// Terminal / Saída
// =======================
let terminal = document.getElementById("terminal");

function limparTerminal() {
    terminal.innerHTML = "";
}

function logTerminal(texto, tipo = "info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.innerHTML = texto;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// =======================
// Execução de Código
// =======================
function executarCodigo() {
    let codigo = editor.getValue();
    logTerminal("> Executando código...", "info");

    fetch("/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codigo })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) logTerminal(data.result, "success");
            else logTerminal("Erro: " + data.error, "error");
        })
        .catch(() => logTerminal("Erro de conexão com o servidor", "error"));
}

// =======================
// Salvar Código
// =======================
function salvarCodigo() {
    let codigo = editor.getValue();
    arquivos[arquivoAtual] = codigo; // salva localmente
    fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codigo })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                logTerminal("✔ Código salvo com sucesso!", "success");
            } else {
                logTerminal("❌ Erro ao salvar: " + data.error, "error");
            }
        });
}

// =======================
// Multi-Abas Dinâmicas
// =======================
function criarAba(nome, conteudo = "") {
    if (arquivos[nome]) return; // já existe
    arquivos[nome] = conteudo;

    // Cria aba
    let tab = document.createElement("div");
    tab.className = "tab";
    tab.textContent = nome;
    tab.onclick = () => abrirAba(nome);

    document.getElementById("tab-bar").appendChild(tab);
    abrirAba(nome);
}

// =======================
// Atalhos do teclado
// =======================
document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "s") {
        e.preventDefault();
        salvarCodigo();
    }
    if (e.ctrlKey && e.key === "Enter") {
        e.preventDefault();
        executarCodigo();
    }
});

// =======================
// Início
// =======================
abrirArquivo("main");
