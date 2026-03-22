// static/js/editor.js

// ===== Inicializa CodeMirror =====
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name: "python", version: 3, singleLineStringErrors: false},
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

// ===== Controle de abas =====
let arquivoAtivo = "main";
function abrirArquivo(nome) {
    if (!arquivos[nome]) {
        logTerminal(`Arquivo '${nome}' não existe`, "error");
        return;
    }
    arquivoAtivo = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

function abrirAba(nome) {
    abrirArquivo(nome);
}

function atualizarAbas() {
    const tabBar = document.getElementById("tab-bar");
    tabBar.innerHTML = "";
    Object.keys(arquivos).forEach(nome => {
        let div = document.createElement("div");
        div.textContent = nome + ".ls";
        div.className = (nome === arquivoAtivo) ? "tab active" : "tab";
        div.onclick = () => abrirArquivo(nome);
        tabBar.appendChild(div);
    });
}

// ===== Terminal / execução =====
let terminal = document.getElementById("terminal");

function limparTerminal() {
    terminal.innerHTML = "";
}

function logTerminal(texto, tipo = "info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.innerHTML = texto.replace(/\n/g, "<br>");
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// ===== Atualiza conteúdo do arquivo ativo =====
function atualizarArquivoAtivo() {
    arquivos[arquivoAtivo] = editor.getValue();
}

// ===== Executar código via API =====
function executarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];
    logTerminal("> Executando...", "info");

    fetch("/run", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            logTerminal(data.result, "success");
        } else {
            logTerminal("Erro: " + data.error, "error");
        }
    })
    .catch(() => logTerminal("Erro conexão servidor", "error"));
}

// ===== Salvar código via API =====
function salvarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];

    fetch("/save", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            logTerminal(`Arquivo '${arquivoAtivo}.ls' salvo com sucesso!`, "success");
        } else {
            logTerminal("Erro ao salvar: " + data.error, "error");
        }
    })
    .catch(() => logTerminal("Erro conexão servidor", "error"));
}

// ===== Adicionar novo arquivo =====
function novoArquivo(nome) {
    if (!nome) {
        logTerminal("Nome de arquivo inválido", "error");
        return;
    }
    nome = nome.replace(/\W/g,"_"); // só letras, números e _
    if (arquivos[nome]) {
        logTerminal(`Arquivo '${nome}' já existe`, "error");
        return;
    }
    arquivos[nome] = "// Novo arquivo\n";
    abrirArquivo(nome);
}

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", () => {
    atualizarAbas();
    abrirArquivo("main");
});
