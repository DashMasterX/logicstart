// ===== LogicStart Elite ULTRA PLUS MAX =====

// Inicializa CodeMirror
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: "javascript", // futuramente pode criar modo "logicstart"
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    tabSize: 4,
    extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-D": function(cm){ cm.execCommand("selectNextOccurrence"); },
        "Ctrl-/": function(cm){ cm.toggleComment(); },
        "Ctrl-S": salvarLocal
    }
});

// ===== Palavras-chave da linguagem em português =====
const LS_KEYWORDS = [
    "imprimir","variável","se","senão","enquanto","para",
    "função","retornar","verdadeiro","falso","nulo"
];
const LS_FUNCS = {
    "imprimir": "Exibe texto ou valor no terminal",
    "variável": "Declara uma variável",
    "se": "Condição verdadeira",
    "enquanto": "Loop enquanto condição verdadeira",
    "função": "Define uma função",
    "retornar": "Retorna um valor"
};

// ===== Multi-arquivos com localStorage =====
let arquivos = JSON.parse(localStorage.getItem("logicstart_arquivos")) || {
    "principal": "// Código principal\n",
    "teste": "// Código de teste\n"
};
let arquivoAtivo = Object.keys(arquivos)[0];

// ===== Terminal =====
let terminal = document.getElementById("terminal");
function logTerminal(msg,tipo="info"){
    let div = document.createElement("div");
    div.className = tipo;
    div.innerHTML = msg.replace(/\n/g,"<br>");
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}
function limparTerminal(){ terminal.innerHTML=""; }

// ===== Arquivos =====
function salvarLocal(){
    atualizarArquivo();
    localStorage.setItem("logicstart_arquivos", JSON.stringify(arquivos));
    logTerminal(`Arquivos salvos localmente`, "success");
}
function atualizarArquivo(){
    arquivos[arquivoAtivo] = editor.getValue();
}
function abrirArquivo(nome){
    if(!arquivos[nome]) return logTerminal(`Arquivo '${nome}' não existe`,"error");
    arquivoAtivo=nome;
    editor.setValue(arquivos[nome]);
    atualizarAbas();
    logTerminal(`Arquivo '${nome}' aberto`,"info");
}
function atualizarAbas(){
    const tabBar=document.getElementById("tab-bar");
    const fileList=document.getElementById("file-list");
    tabBar.innerHTML="";
    fileList.innerHTML="";
    Object.keys(arquivos).forEach(nome=>{
        // Abas
        let tab=document.createElement("div");
        tab.textContent=nome+".ls";
        tab.className=(nome===arquivoAtivo)?"tab active":"tab";
        tab.onclick=()=>abrirArquivo(nome);
        tabBar.appendChild(tab);
        // Lista lateral
        let fdiv=document.createElement("div");
        fdiv.textContent=nome+".ls";
        fdiv.className=(nome===arquivoAtivo)?"active":"";
        fdiv.onclick=()=>abrirArquivo(nome);
        fileList.appendChild(fdiv);
    });
}

// ===== Novo e remover =====
function novoArquivo(){
    let nome=prompt("Nome do novo arquivo:").replace(/\W/g,"_");
    if(!nome||arquivos[nome]) return logTerminal("Arquivo inválido ou já existe","error");
    arquivos[nome]="// Novo arquivo\n";
    arquivoAtivo=nome;
    atualizarAbas();
    editor.setValue(arquivos[nome]);
    salvarLocal();
}
function removerArquivo(){
    if(arquivoAtivo==="principal") return logTerminal("Não é possível remover o arquivo principal","error");
    delete arquivos[arquivoAtivo];
    arquivoAtivo=Object.keys(arquivos)[0];
    abrirArquivo(arquivoAtivo);
    salvarLocal();
}

// ===== Executar código =====
function executarCodigo(){
    atualizarArquivo();
    let code = editor.getValue();
    logTerminal("> Executando código...","info");
    try{
        // Simulação: apenas eval JS para teste
        let result = eval(code);
        logTerminal(result!==undefined?result:"Executado","success");
    }catch(e){
        logTerminal(e,"error");
    }
}

// ===== Download / Upload =====
function baixarArquivo(){
    atualizarArquivo();
    let blob = new Blob([arquivos[arquivoAtivo]], {type:"text/plain"});
    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = arquivoAtivo+".ls";
    a.click();
}
function uploadArquivo(){
    let input=document.getElementById("upload-input");
    input.click();
    input.onchange=e=>{
        let file=e.target.files[0];
        if(!file) return;
        let reader=new FileReader();
        reader.onload=function(evt){
            let nome=file.name.replace(/\W/g,"_").replace(/\.ls$/,"");
            arquivos[nome]=evt.target.result;
            arquivoAtivo=nome;
            atualizarAbas();
            editor.setValue(evt.target.result);
            salvarLocal();
            logTerminal(`Arquivo '${file.name}' importado`,"success");
        };
        reader.readAsText(file);
        input.value="";
    };
}

// ===== Autocomplete Contextual =====
CodeMirror.registerHelper("hint","anyword",function(cm){
    let cur=cm.getCursor();
    let token=cm.getTokenAt(cur);
    let start=token.start, end=cur.ch;
    let word=token.string.slice(0,end-start).toLowerCase();
    let list = LS_KEYWORDS.filter(k=>k.startsWith(word));
    return {list:list, from:CodeMirror.Pos(cur.line,start), to:CodeMirror.Pos(cur.line,end)};
});

// ===== Botões =====
document.getElementById("run-btn").onclick=executarCodigo;
document.getElementById("run-float").onclick=executarCodigo;
document.getElementById("save-btn").onclick=salvarLocal;
document.getElementById("save-float").onclick=salvarLocal;
document.getElementById("clear-btn").onclick=limparTerminal;
document.getElementById("clear-float").onclick=limparTerminal;
document.getElementById("new-btn").onclick=novoArquivo;
document.getElementById("del-btn").onclick=removerArquivo;
document.getElementById("download-btn").onclick=baixarArquivo;
document.getElementById("upload-btn").onclick=uploadArquivo;

// ===== Inicialização =====
abrirArquivo(arquivoAtivo);
