# main.py

from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from gui.screens import EditorScreen, ResultScreen
from executor import Executor

# Se estiver no PC, define tamanho da janela
Window.size = (900, 600)

class LogicStartApp(MDApp):
    def build(self):
        self.sm = ScreenManager()

        # Inicializa telas
        self.editor_screen = EditorScreen(app=self, name="editor")
        self.result_screen = ResultScreen(app=self, name="resultado")

        self.sm.add_widget(self.editor_screen)
        self.sm.add_widget(self.result_screen)

        return self.sm

    def execute_code(self, codigo):
        """
        Executa o código do editor e mostra no resultado.
        """
        try:
            executor = Executor(codigo)
            resultado = executor.executar()
        except Exception as e:
            resultado = f"❌ Erro: {e}"

        self.result_screen.show_output(str(resultado))


def main():
    LogicStartApp().run()


if __name__ == "__main__":
    main()
