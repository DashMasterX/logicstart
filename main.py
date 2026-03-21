from engine import LogicStart

codigo = """
guardar x = 5

repetir 3 vezes
  mostrar x
"""

logic = LogicStart(codigo)
logic.executar()