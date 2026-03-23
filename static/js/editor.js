// static/js/editor.js - LogicStart Elite Pro Max Plus

// ===== Inicializa CodeMirror =====
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name:"python", version:3, singleLineStringErrors:false},
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: true,
    styleActiveLine: true,
    matchBrackets: true
});

// ===== Arquivos simulados =====
let arquivos = {
    "main": "# Seu código LogicStart aqui\n",
    "teste": "// Código de teste\n"
};
let arquivoAtivo = "main";

// ===== Terminal =====
let terminal = document.getElementById("terminal");

function limparTerminal() {
    terminal.innerHTML = "";
}

function logTerminal(texto, tipo="info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.innerHTML = texto.replace(/\n/g, "<br>");
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// ===== Abas e gerenciamento de arquivos =====
function atualizarAbas() {
    const tabBar = document.getElementById("tab-bar");
    tabBar.innerHTML = "";

    Object.keys(arquivos).forEach(nome => {
        let div = document.createElement("div");
        div.textContent = nome + ".ls";
        div.className = (nome === arquivoAtivo) ? "tab active" : "tab";

        // Selecionar arquivo ao clicar
        div.onclick = () => abrirArquivo(nome);

        // Arrastar e soltar para reorganizar abas
        div.draggable = true;
        div.ondragstart = (e) => e.dataTransfer.setData("text", nome);
        div.ondragover = (e) => e.preventDefault();
        div.ondrop = (e) => {
            const from = e.dataTransfer.getData("text");
            const to = nome;
            if (from !== to) {
                let keys = Object.keys(arquivos);
                keys.splice(keys.indexOf(from), 1);
                keys.splice(keys.indexOf(to), 0, from);
                let novosArquivos = {};
                keys.forEach(k => novosArquivos[k] = arquivos[k]);
                arquivos = novosArquivos;
                atualizarAbas();
            }
        };

        tabBar.appendChild(div);
    });
}

function abrirArquivo(nome) {
    if (!arquivos[nome]) return logTerminal(`Arquivo '${nome}' não existe`, "error");
    atualizarArquivoAtivo();
    arquivoAtivo = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

function abrirAba(nome) { abrirArquivo(nome); }

function atualizarArquivoAtivo() {
    arquivos[arquivoAtivo] = editor.getValue();
}

// ===== Executar código via API =====
function executarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];

    logTerminal(`> Executando '${arquivoAtivo}.ls'...`, "info");

    fetch("/run", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) logTerminal(data.result, "success");
        else logTerminal("Erro: " + data.error, "error");
    })
    .catch(() => logTerminal("Erro de conexão com o servidor", "error"));
}

// ===== Salvar código via API =====
function salvarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];

    fetch("/save", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) logTerminal(`Arquivo '${arquivoAtivo}.ls' salvo com sucesso!`, "success");
        else logTerminal("Erro ao salvar: " + data.error, "error");
    })
    .catch(() => logTerminal("Erro de conexão com o servidor", "error"));
}

// ===== Criar novo arquivo =====
function novoArquivo() {
    let nome = prompt("Nome do novo arquivo (somente letras/números/underscores):");
    if (!nome) return;
    nome = nome.replace(/\W/g,"_");
    if (arquivos[nome]) return logTerminal(`Arquivo '${nome}' já existe`, "error");

    arquivos[nome] = "// Novo arquivo\n";
    abrirArquivo(nome);
    logTerminal(`Arquivo '${nome}.ls' criado!`, "success");
}

// ===== Remover arquivo =====
function removerArquivo() {
    if (arquivoAtivo === "main") return logTerminal("Não é possível remover o arquivo main", "error");

    logTerminal(`Arquivo '${arquivoAtivo}.ls' removido`, "info");
    delete arquivos[arquivoAtivo];
    arquivoAtivo = Object.keys(arquivos)[0];
    abrirArquivo(arquivoAtivo);
}

// ===== Botões flutuantes =====
document.getElementById("run-btn").onclick = executarCodigo;
document.getElementById("save-btn").onclick = salvarCodigo;
document.getElementById("clear-btn").onclick = limparTerminal;

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", () => {
    atualizarAbas();
    abrirArquivo("main");
    logTerminal("LogicStart Elite Pro Max Plus inicializado!", "info");
});
