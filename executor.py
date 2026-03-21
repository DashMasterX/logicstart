import io, sys

class Executor:
    def __init__(self, codigo):
        self.codigo = codigo

    def executar(self):
        buffer = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buffer
        try:
            exec(self.codigo, {"__builtins__": {}})
        finally:
            sys.stdout = old_stdout
        return buffer.getvalue() or "✔ Executado com sucesso"
