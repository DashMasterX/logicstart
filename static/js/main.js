const editor = document.getElementById("editor");
const output = document.getElementById("output");

document.getElementById("run").addEventListener("click", async () => {
    output.textContent = "⏳ Executando...";
    const code = editor.value;

    try {
        const res = await fetch("/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code })
        });
        const data = await res.json();
        output.textContent = data.result || data.error;
    } catch (e) {
        output.textContent = "💥 Erro na execução";
    }
});

document.getElementById("clear").addEventListener("click", () => {
    editor.value = "";
    output.textContent = "";
});
