// static/js/editor.js - LogicStart Elite Pro Max Plus (estilo Pydroid 3)

// ===== Inicializa CodeMirror =====
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name:"python", version:3, singleLineStringErrors:false},
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
});

// ===== Arquivos e armazenamento =====
let arquivos = JSON.parse(localStorage.getItem("ls_arquivos")) || {
    "main": "# Seu código LogicStart aqui\n",
};
let arquivoAtivo = Object.keys(arquivos)[0];

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

// ===== Abas e painel lateral =====
function atualizarAbas() {
    const tabBar = document.getElementById("tab-bar");
    const fileList = document.getElementById("file-list");
    tabBar.innerHTML = "";
    fileList.innerHTML = "";

    Object.keys(arquivos).forEach(nome => {
        // Aba
        let aba = document.createElement("div");
        aba.textContent = nome + ".ls";
        aba.className = (nome === arquivoAtivo) ? "tab active" : "tab";
        aba.onclick = () => abrirArquivo(nome);
        aba.draggable = true;

        // Drag & drop de abas
        aba.ondragstart = e => e.dataTransfer.setData("text", nome);
        aba.ondragover = e => e.preventDefault();
        aba.ondrop = e => {
            let from = e.dataTransfer.getData("text");
            if (from === nome) return;
            let keys = Object.keys(arquivos);
            keys.splice(keys.indexOf(from),1);
            keys.splice(keys.indexOf(nome),0,from);
            let newArquivos = {};
            keys.forEach(k => newArquivos[k] = arquivos[k]);
            arquivos = newArquivos;
            atualizarAbas();
            salvarLocal();
        };
        tabBar.appendChild(aba);

        // Lista lateral
        let item = document.createElement("div");
        item.textContent = nome + ".ls";
        item.className = (nome === arquivoAtivo) ? "active" : "";
        item.onclick = () => abrirArquivo(nome);
        fileList.appendChild(item);
    });
}

// ===== Abrir arquivo =====
function abrirArquivo(nome) {
    if (!arquivos[nome]) return logTerminal(`Arquivo '${nome}' não existe.`, "error");
    arquivoAtivo = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

// ===== Atualizar arquivo ativo =====
function atualizarArquivoAtivo() {
    arquivos[arquivoAtivo] = editor.getValue();
    salvarLocal();
}

// ===== Salvar no localStorage =====
function salvarLocal() {
    localStorage.setItem("ls_arquivos", JSON.stringify(arquivos));
}

// ===== Novo arquivo =====
function novoArquivo() {
    let nome = prompt("Nome do novo arquivo (letras, números, underscores):");
    if (!nome) return;
    nome = nome.replace(/\W/g,"_");
    if (arquivos[nome]) return logTerminal(`Arquivo '${nome}' já existe!`, "error");
    arquivos[nome] = "// Novo arquivo\n";
    arquivoAtivo = nome;
    abrirArquivo(nome);
    salvarLocal();
}

// ===== Remover arquivo =====
function removerArquivo() {
    if (arquivoAtivo === "main") return logTerminal("Não é possível remover o main.", "error");
    delete arquivos[arquivoAtivo];
    arquivoAtivo = Object.keys(arquivos)[0];
    abrirArquivo(arquivoAtivo);
    salvarLocal();
}

// ===== Executar código simulado =====
function executarCodigo() {
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];
    logTerminal("> Executando código...", "info");

    try {
        // Simula execução do código
        let resultado = "Resultado da execução:\n" + codigo.split("\n").map((l,i)=>`${i+1}: ${l}`).join("\n");
        logTerminal(resultado, "success");
    } catch(e) {
        logTerminal("Erro: " + e.message, "error");
    }
}

// ===== Salvar código no celular (download) =====
function salvarCodigo() {
    atualizarArquivoAtivo();
    let blob = new Blob([arquivos[arquivoAtivo]], {type:"text/plain"});
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    a.download = arquivoAtivo + ".ls";
    a.click();
    URL.revokeObjectURL(url);
    logTerminal(`Arquivo '${arquivoAtivo}.ls' salvo no dispositivo.`, "success");
}

// ===== Importar arquivo do celular =====
function importarArquivo() {
    let input = document.createElement("input");
    input.type = "file";
    input.accept = ".ls,.txt";
    input.onchange = () => {
        let file = input.files[0];
        if (!file) return;
        let reader = new FileReader();
        reader.onload = () => {
            let nome = file.name.replace(/\W/g,"_").replace(/\.ls$|\.txt$/i,"");
            arquivos[nome] = reader.result;
            arquivoAtivo = nome;
            abrirArquivo(nome);
            salvarLocal();
            logTerminal(`Arquivo '${file.name}' importado!`, "success");
        };
        reader.readAsText(file);
    };
    input.click();
}

// ===== Menu três pontinhos =====
const menuBtn = document.querySelector(".menu-btn");
const menuContent = document.querySelector(".menu-content");
menuBtn.addEventListener("click", () => {
    menuContent.style.display = menuContent.style.display === "block" ? "none" : "block";
});
document.addEventListener("click", e => {
    if (!menuBtn.contains(e.target) && !menuContent.contains(e.target)) {
        menuContent.style.display = "none";
    }
});

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", () => {
    atualizarAbas();
    abrirArquivo(arquivoAtivo);

    // Botões flutuantes
    document.getElementById("run-float").onclick = executarCodigo;
    document.getElementById("save-float").onclick = salvarCodigo;
    document.getElementById("clear-float").onclick = limparTerminal;
});
