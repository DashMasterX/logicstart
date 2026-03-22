let terminal = {
    el: document.getElementById("terminal"),
    limpar: function(){ this.el.innerHTML = ""; },
    log: function(msg, tipo="info"){
        let div = document.createElement("div");
        div.className = tipo;
        div.innerHTML = msg;
        this.el.appendChild(div);
        this.el.scrollTop = this.el.scrollHeight;
    }
};

function executarCodigo(){
    let codigo = editor.getValue();
    terminal.log("> Executando...", "info");
    fetch("/run", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) terminal.log(data.result, "success");
        else terminal.log("Erro: "+data.error, "error");
    })
    .catch(()=>terminal.log("Erro conexão servidor","error"));
}

function salvarCodigo(){
    let codigo = editor.getValue();
    fetch("/save", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code: codigo})
    })
    .then(res=>res.json())
    .then(data=>{
        alert(data.success ? "Código salvo!" : data.error);
    });
}
