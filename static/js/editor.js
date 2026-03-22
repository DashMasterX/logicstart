// Inicializa CodeMirror
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    mode: {name:"python", version:3, singleLineStringErrors:false},
    theme: "dracula",
    lineNumbers: true,
    lineWrapping: true,
    indentUnit: 4,
    tabSize: 4,
});

// Arquivos simulados
let arquivos = {
    "main": "# Seu código LogicStart aqui\n",
    "teste": "// Código de teste\n"
};

function abrirArquivo(nome){
    editor.setValue(arquivos[nome]);
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    let tab = document.querySelector(`.tab[data-file="${nome}"]`);
    if(tab) tab.classList.add("active");
}

// Aba clicada
document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => abrirArquivo(tab.dataset.file));
});

// Painel lateral clicado
document.querySelectorAll("#file-list div").forEach(div => {
    div.addEventListener("click", () => abrirArquivo(div.dataset.file));
});

// Botões
document.getElementById("btnRun").addEventListener("click", executarCodigo);
document.getElementById("btnSave").addEventListener("click", salvarCodigo);
document.getElementById("btnClear").addEventListener("click", () => terminal.limpar());
