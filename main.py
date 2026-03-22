# main.py

import sys
from rich.console import Console
from prompt_toolkit import prompt
from security import Security
from engine import LogicStart, LogicStartErro

console = Console()

def mostrar_boas_vindas():
    console.print("\n[bold cyan]=== LogicStart Pro Max ===[/bold cyan]")
    console.print("[green]Python em Português - IDE Segura[/green]\n")
    console.print("Digite 'sair' para encerrar a sessão.\n")

def main():
    mostrar_boas_vindas()
    seguranca = Security()

    while True:
        try:
            codigo = prompt("[bold yellow]LogicStart > [/bold yellow]\n", multiline=True)
            if codigo.strip().lower() == "sair":
                console.print("[red]Saindo...[/red]")
                break

            # Segurança: verifica código antes de executar
            try:
                seguranca.verificar(codigo)
            except ValueError as ve:
                console.print(f"[bold red]Erro de segurança:[/bold red] {ve}")
                continue

            # Executa engine em português
            engine = LogicStart(codigo)
            try:
                engine.executar()
            except LogicStartErro as le:
                console.print(f"[bold red]Erro na execução:[/bold red] {le}")

        except KeyboardInterrupt:
            console.print("\n[red]Sessão interrompida pelo usuário[/red]")
            break
        except EOFError:
            console.print("\n[red]Sessão encerrada[/red]")
            break
        except Exception as e:
            console.print(f"[bold red]Erro inesperado:[/bold red] {e}")

if __name__ == "__main__":
    main()
