PALAVRAS_RESERVADAS = {
    "mostrar", "guardar", "se", "senão", "repetir", "perguntar"
}

MAX_LOOP = 1000

def validar_nome(nome):
    if not nome.isidentifier():
        return False
    if nome in PALAVRAS_RESERVADAS:
        return False
    return True