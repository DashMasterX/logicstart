from nodes import *

def parse(linhas):
    i = 0
    ast = []

    while i < len(linhas):
        linha = linhas[i].strip()

        if linha.startswith("mostrar"):
            valor = linha.split(" ", 1)[1]
            ast.append(Mostrar(valor))

        elif linha.startswith("guardar"):
            nome, valor = linha.replace("guardar ", "").split("=")
            ast.append(Guardar(nome.strip(), valor.strip()))

        elif linha.startswith("repetir"):
            vezes = int(linha.split()[1])
            i += 1
            bloco = []

            while i < len(linhas) and linhas[i].startswith("  "):
                bloco.append(linhas[i][2:])
                i += 1

            ast.append(Repetir(vezes, parse(bloco)))
            continue

        i += 1

    return ast