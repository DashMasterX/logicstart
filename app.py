# app.py | LogicStart Elite - Nível Empresa Apple Pro Max

from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivymd.app import MDApp
from kivymd.theming import ThemeManager
from executor_nodes import ExecutorNodes
from nodes import Mostrar, Guardar, Repetir, Condicao, Funcao, Retorna, Enquanto, SeSenao
from security import Security
from errors import LogicStartErro

# =============================
# Telas do App
# =============================
class LoginScreen(Screen):
    def login_email(self, email, senha):
        if email and senha:
            self.manager.current = "editor"
        else:
            self.ids.error.text = "Preencha todos os campos"

    def login_guest(self):
        self.manager.current = "editor"

class EditorScreen(Screen):
    def executar_codigo(self):
        codigo = self.ids.editor_input.text.strip()
        if not codigo:
            self.manager.get_screen("resultado").mostrar_saida("⚠ Nenhum código inserido")
            self.manager.current = "resultado"
            return

        try:
            # Validar segurança
            Security().verificar(codigo)

            # Transformar em nodes fictício para teste
            nodes = [
                Mostrar("Olá mundo"),
                Guardar("x", "10"),
                Mostrar("x")
            ]
            executor = ExecutorNodes(nodes)
            resultado = executor.executar()
            self.manager.get_screen("resultado").mostrar_saida(resultado)
            self.manager.current = "resultado"
        except LogicStartErro as e:
            self.manager.get_screen("resultado").mostrar_saida(f"Erro: {e}")
            self.manager.current = "resultado"
        except Exception as e:
            self.manager.get_screen("resultado").mostrar_saida(f"Erro inesperado: {e}")
            self.manager.current = "resultado"

class ResultScreen(Screen):
    def mostrar_saida(self, texto):
        self.ids.result_output.text = texto

# =============================
# Gerenciador de telas
# =============================
class LSManager(ScreenManager):
    pass

# =============================
# App Principal
# =============================
KV = """
LSManager:
    LoginScreen:
        name: "login"
        id: login
    EditorScreen:
        name: "editor"
        id: editor
    ResultScreen:
        name: "resultado"
        id: resultado

<LoginScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: 20
        spacing: 20
        MDLabel:
            text: "🚀 LogicStart Elite"
            halign: "center"
            font_style: "H4"
        MDTextField:
            id: email
            hint_text: "Email"
        MDTextField:
            id: senha
            hint_text: "Senha"
            password: True
        MDBoxLayout:
            spacing: 10
            MDRectangleFlatButton:
                text: "Entrar"
                on_release: root.login_email(email.text, senha.text)
            MDRectangleFlatButton:
                text: "Guest"
                on_release: root.login_guest()
        MDLabel:
            id: error
            text: ""
            theme_text_color: "Error"

<EditorScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: 12
        spacing: 12
        MDLabel:
            text: "💻 Editor LogicStart"
            halign: "center"
            font_style: "H5"
        MDTextField:
            id: editor_input
            hint_text: "Digite seu código aqui..."
            multiline: True
        MDBoxLayout:
            size_hint_y: None
            height: 60
            spacing: 10
            MDRaisedButton:
                text: "▶ Executar"
                on_release: root.executar_codigo()
            MDRaisedButton:
                text: "🧹 Limpar"
                on_release: editor_input.text=""
            MDIconButton:
                icon: "content-copy"
                on_release: app.copiar_resultado()

<ResultScreen>:
    MDBoxLayout:
        orientation: "vertical"
        padding: 12
        spacing: 12
        MDLabel:
            text: "📄 Resultado"
            halign: "center"
            font_style: "H5"
        MDTextField:
            id: result_output
            hint_text: "Resultado..."
            multiline: True
            readonly: True
        MDRaisedButton:
            text: "⬅ Voltar"
            pos_hint: {"center_x":0.5}
            on_release: app.voltar_editor()
"""

class LogicStartApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.sm = Builder.load_string(KV)
        return self.sm

    def copiar_resultado(self):
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.sm.get_screen("resultado").ids.result_output.text)

    def voltar_editor(self):
        self.sm.transition = SlideTransition(direction="right")
        self.sm.current = "editor"

if __name__ == "__main__":
    LogicStartApp().run()
