// static/js/editor.js - LogicStart Elite Plus Mobile Ready

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

// ===== Arquivos locais =====
let arquivos = JSON.parse(localStorage.getItem("arquivos")) || {
    "main": "# Seu código LogicStart aqui\n",
    "teste": "// Código de teste\n"
};
let arquivoAtivo = "main";

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

// ===== Abas e gerenciamento =====
function atualizarAbas() {
    const tabBar = document.getElementById("tab-bar");
    tabBar.innerHTML = "";

    Object.keys(arquivos).forEach(nome => {
        let div = document.createElement("div");
        div.textContent = nome + ".ls";
        div.className = (nome === arquivoAtivo) ? "tab active" : "tab";

        div.onclick = () => abrirArquivo(nome);

        // Drag & Drop para reorganizar
        div.draggable = true;
        div.ondragstart = (e) => e.dataTransfer.setData("text", nome);
        div.ondragover = (e) => e.preventDefault();
        div.ondrop = (e) => {
            const from = e.dataTransfer.getData("text");
            const to = nome;
            if(from !== to){
                let keys = Object.keys(arquivos);
                keys.splice(keys.indexOf(from), 1);
                keys.splice(keys.indexOf(to), 0, from);
                let novos = {};
                keys.forEach(k => novos[k] = arquivos[k]);
                arquivos = novos;
                salvarArquivos();
                atualizarAbas();
            }
        };

        tabBar.appendChild(div);
    });
}

function abrirArquivo(nome) {
    if(!arquivos[nome]) return logTerminal(`Arquivo '${nome}' não existe`, "error");
    atualizarArquivoAtivo();
    arquivoAtivo = nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
}

function abrirAba(nome){ abrirArquivo(nome); }
function atualizarArquivoAtivo(){ arquivos[arquivoAtivo] = editor.getValue(); salvarArquivos(); }

// ===== Salvar arquivos no LocalStorage =====
function salvarArquivos(){
    localStorage.setItem("arquivos", JSON.stringify(arquivos));
}

// ===== Criar novo arquivo =====
function novoArquivo(){
    let nome = prompt("Nome do novo arquivo (somente letras/números/_):");
    if(!nome) return;
    nome = nome.replace(/\W/g,"_");
    if(arquivos[nome]) return logTerminal(`Arquivo '${nome}' já existe`, "error");
    arquivos[nome] = "// Novo arquivo\n";
    abrirArquivo(nome);
    logTerminal(`Arquivo '${nome}.ls' criado!`, "success");
}

// ===== Remover arquivo =====
function removerArquivo(){
    if(arquivoAtivo === "main") return logTerminal("Não é possível remover o main", "error");
    logTerminal(`Arquivo '${arquivoAtivo}.ls' removido`, "info");
    delete arquivos[arquivoAtivo];
    arquivoAtivo = Object.keys(arquivos)[0];
    abrirArquivo(arquivoAtivo);
}

// ===== Download do arquivo atual =====
function baixarArquivo(){
    atualizarArquivoAtivo();
    const blob = new Blob([arquivos[arquivoAtivo]], {type:"text/plain"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = arquivoAtivo + ".ls";
    link.click();
    logTerminal(`Arquivo '${arquivoAtivo}.ls' baixado!`, "success");
}

// ===== Upload de arquivo =====
function carregarArquivo(input){
    const file = input.files[0];
    if(!file) return;
    const reader = new FileReader();
    reader.onload = function(e){
        let nome = file.name.replace(/\W/g,"_").replace(/\.ls$/,"");
        arquivos[nome] = e.target.result;
        abrirArquivo(nome);
        logTerminal(`Arquivo '${file.name}' carregado!`, "success");
    }
    reader.readAsText(file);
    input.value = "";
}

// ===== Executar código local simulado =====
function executarCodigo(){
    atualizarArquivoAtivo();
    let codigo = arquivos[arquivoAtivo];
    logTerminal(`> Executando '${arquivoAtivo}.ls' (simulado)...`, "info");
    try{
        // Aqui você pode adicionar a execução real do seu parser
        logTerminal("Resultado simulado:\n" + codigo, "success");
    }catch(e){
        logTerminal("Erro: " + e.message, "error");
    }
}

// ===== Botões flutuantes =====
document.getElementById("run-btn").onclick = executarCodigo;
document.getElementById("save-btn").onclick = atualizarArquivoAtivo;
document.getElementById("clear-btn").onclick = limparTerminal;

// ===== Inicialização =====
document.addEventListener("DOMContentLoaded", ()=>{
    atualizarAbas();
    abrirArquivo("main");
    logTerminal("LogicStart Elite Mobile Ready inicializado!", "info");
});
