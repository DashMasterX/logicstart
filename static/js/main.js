const editorContainer = document.getElementById("editor-container");
const outputContainer = document.getElementById("output-container");
const editor = document.getElementById("editor");
const output = document.getElementById("output");

document.getElementById("run").addEventListener("click", async () => {
    output.textContent = "⏳ Executando...";
    editorContainer.classList.replace("fade-in","fade-out");
    outputContainer.classList.replace("fade-out","fade-in");

    try {
        const res = await fetch("/run", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: editor.value })
        });
        const data = await res.json();
        output.textContent = data.result || data.error;
    } catch (e) {
        output.textContent = "💥 Erro na execução";
    }
});

document.getElementById("back").addEventListener("click", () => {
    outputContainer.classList.replace("fade-in","fade-out");
    editorContainer.classList.replace("fade-out","fade-in");
});
