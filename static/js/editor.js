// static/js/editor.js - IDE avançado LogicStart Elite Pro Max

// ===== Inicializa CodeMirror =====
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

// ===== Controle de abas =====
let arquivoAtivo = "main";

function atualizarAbas() {
    const tabBar = document.getElementById("tab-bar");
    tabBar.innerHTML = "";
    Object.keys(arquivos).forEach(nome => {
        let div = document.createElement("div");
        div.textContent = nome + ".ls";
        div.className = (nome === arquivoAtivo) ? "tab active" : "tab";
        div.onclick = () => abrirArquivo(nome);
        div.draggable = true;
        div.ondragstart = (e) => e.dataTransfer.setData("text", nome);
        div.ondragover = (e) => e.preventDefault();
        div.ondrop = (e) => {
            const arr = Object.keys(arquivos);
            const arrCopy = [...arr];
            const from = e.dataTransfer.getData("text");
            const to = nome;
            if (from !== to) {
                arrCopy.splice(arrCopy.indexOf(from),1);
                arrCopy.splice(arrCopy.indexOf(to),0,from);
                let novosArquivos = {};
                arrCopy.forEach(n => novosArquivos[n] = arquivos[n]);
                arquivos = novosArquivos;
                atualizarAbas();
            }
        };
        tabBar.appendChild(div);
    });
}

function abrirArquivo(nome) {
    if (!arquivos[nome]) return logTerminal(`Arquivo '${nome}' não existe`, "error");
    arquivoAtivo = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

function abrirAba(nome) { abrirArquivo(nome); }

// ===== Terminal =====
let terminal = document.getElementById("terminal");
function limparTerminal() { terminal.innerHTML = ""; }
function logTerminal(texto, tipo="info") {
    let div = document.createElement("div");
    div.className = tipo;
    div.innerHTML = texto.replace(/\n/g,"<br>");
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

// ===== Atualiza arquivo ativo =====
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
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) logTerminal(data.result, "success");
        else logTerminal("Erro: " + data.error, "error");
    })
    .catch(() => logTerminal("Erro conexão servidor","error"));
}

// ===== Salvar código via API =====
function salvarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];

    fetch("/save", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) logTerminal(`Arquivo '${arquivoAtivo}.ls' salvo com sucesso!`, "success");
        else logTerminal("Erro ao salvar: " + data.error, "error");
    })
    .catch(()=>logTerminal("Erro conexão servidor","error"));
}

// ===== Criar novo arquivo =====
function novoArquivo() {
    let nome = prompt("Nome do novo arquivo (somente letras/números/underscores):");
    if (!nome) return;
    nome = nome.replace(/\W/g,"_");
    if (arquivos[nome]) return logTerminal(`Arquivo '${nome}' já existe`, "error");
    arquivos[nome] = "// Novo arquivo\n";
    abrirArquivo(nome);
}

// ===== Remover arquivo =====
function removerArquivo() {
    if (arquivoAtivo === "main") return logTerminal("Não é possível remover o main", "error");
    delete arquivos[arquivoAtivo];
    arquivoAtivo = Object.keys(arquivos)[0];
    abrirArquivo(arquivoAtivo);
}

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", () => {
    atualizarAbas();
    abrirArquivo("main");
});
