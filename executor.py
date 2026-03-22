# executor.py
import io
import sys
import traceback
from security import Security
from errors import LogicStartExecucaoErro

class Executor:
    """
    Executor seguro para o código LogicStart.
    Suporta Python em português inteligente.
    """

    def __init__(self, codigo: str):
        self.codigo = codigo
        self.security = Security()  # Verificador de segurança
        self.saida = ""

    def executar(self) -> str:
        """
        Executa o código de forma segura, capturando a saída e erros.
        Retorna a saída do código.
        Lança LogicStartExecucaoErro se houver falha.
        """
        try:
            # Verifica segurança antes de executar
            self.security.verificar(self.codigo)

            # Redireciona stdout
            buffer = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = buffer

            # Ambiente seguro limitado
            ambiente = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "int": int,
                    "float": float,
                    "str": str,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                    # Adicione outras funções seguras que quiser
                }
            }

            # Executa o código
            exec(self.codigo, ambiente)

            # Captura saída
            self.saida = buffer.getvalue()
            return self.saida or "✔ Executado com sucesso"

        except Exception as e:
            # Captura traceback e lança erro customizado
            tb = traceback.format_exc()
            raise LogicStartExecucaoErro(-1, f"{str(e)}\n{tb}") from e

        finally:
            # Restaura stdout
            sys.stdout = old_stdout
