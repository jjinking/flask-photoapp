import os
from base64 import b64encode
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen

class UserCred(object):
    data_dir = App().user_data_dir
    store = JsonStore(os.path.join(data_dir, 'login.json'))

    @staticmethod
    def store_cred(email, password):
        UserCred.store.put('credentials',
                           email=email,
                           password=password)

    @staticmethod
    def load_cred():
        '''
        Load user-email, password
        '''
        try:
            creds = UserCred.store.get('credentials')
        except:
            return "", ""

        try:
            email = creds['email']
        except KeyError:
            email = ""

        try:
            password = creds['password']
        except KeyError:
            password = ""

        return email, password

class LoginScreen(Screen):
    def login(self):
        email = self.login_email.text
        password = self.login_password.text
        UserCred.store_cred(email, password)
        
        print "loaded", UserCred.load_cred()
        
class PostsScreen(Screen):
    def get_api_headers(self, username, password):
        return {
            'Authorization': 'Basic ' + b64encode(
                (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_posts(self):
        e1, p1 = UserCred.load_cred()
        url = 'http://127.0.0.1:5000/api/v1.0/posts/'
        req = UrlRequest(url,
                         on_success=lambda: "success!",
                         on_failure=lambda: "failure!",
                         on_error=lambda: "error!",
                         req_headers=self.get_api_headers())

class PhotoAppScreenManager(ScreenManager):
    pass

class PhotoApp(App):
    def build(self):
        return PhotoAppScreenManager()


if __name__ == '__main__':
    PhotoApp().run()
