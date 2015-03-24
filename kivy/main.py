from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

class LoginScreen(Screen):
    pass

class PhotoAppScreenManager(ScreenManager):
    pass

class PhotoApp(App):
    def build(self):
        return PhotoAppScreenManager()


if __name__ == '__main__':
    PhotoApp().run()
