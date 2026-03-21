from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard

class EditorScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = MDBoxLayout(orientation="vertical", padding=12, spacing=12)

        titulo = MDLabel(text="🚀 LogicStart IDE", halign="center", font_style="H4")
        self.input = MDTextField(hint_text="Digite seu código...", multiline=True, size_hint_y=0.8)
        editor_card = MDCard(orientation="vertical", padding=12, radius=[20], elevation=10)
        editor_card.add_widget(self.input)

        botoes = MDBoxLayout(size_hint_y=None, height=60, spacing=10)
        self.btn_run = MDRaisedButton(text="▶ Executar", on_press=self.run_code)
        self.btn_clear = MDRaisedButton(text="🧹 Limpar", on_press=lambda x: self.input.text.clear())
        self.btn_copy = MDIconButton(icon="content-copy", on_press=self.copy_output)
        for b in [self.btn_run, self.btn_clear, self.btn_copy]: botoes.add_widget(b)

        layout.add_widget(titulo)
        layout.add_widget(editor_card)
        layout.add_widget(botoes)
        self.add_widget(layout)

    def run_code(self, instance):
        Animation(opacity=0.5, duration=0.1).start(self.btn_run)
        Animation(opacity=1, duration=0.1).start(self.btn_run)
        code = self.input.text.strip()
        if not code:
            self.app.result_screen.show_output("⚠️ Nenhum código inserido")
        else:
            self.app.sm.transition = SlideTransition(direction="left")
            self.app.sm.current = "resultado"
            Clock.schedule_once(lambda dt: self.app.execute_code(code), 0.2)

    def copy_output(self, instance):
        Clipboard.copy(self.app.result_screen.output.text)


class ResultScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        layout = MDBoxLayout(orientation="vertical", padding=12, spacing=12)
        titulo = MDLabel(text="💻 Resultado", halign="center", font_style="H5")

        self.output = MDTextField(hint_text="Resultado...", multiline=True, readonly=True)
        output_card = MDCard(orientation="vertical", padding=12, radius=[20], elevation=10)
        output_card.add_widget(self.output)

        btn_back = MDRaisedButton(text="⬅ Voltar", pos_hint={"center_x":0.5}, on_press=self.back)
        layout.add_widget(titulo)
        layout.add_widget(output_card)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def show_output(self, texto):
        self.output.text = texto

    def back(self, instance):
        self.app.sm.transition = SlideTransition(direction="right")
        self.app.sm.current = "editor"
