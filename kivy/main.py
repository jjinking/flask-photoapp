from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget


class LoginScreen(BoxLayout):
    pass

class PhotoApp(App):
    def build(self):
        return LoginScreen()


if __name__ == '__main__':
    PhotoApp().run()
