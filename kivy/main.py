import os
from base64 import b64encode
from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from kivy.properties import ObjectProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
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
            email = creds['email']
            password = creds['password']
        except:
            return "", ""

        return email, password

class WebApi(object):
    
    url = 'http://127.0.0.1:5000/api/v1.0/'
    url_posts = url + 'posts/'
    
    @staticmethod
    def _get_headers():
        email, pw = UserCred.load_cred()
        return {
            'Authorization': 'Basic ' + b64encode(
                (email + ':' + pw).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
    @staticmethod
    def posts(on_success, on_failure, on_error):
        req = UrlRequest(WebApi.url_posts,
                         on_success=on_success,
                         on_failure=on_failure,
                         on_error=on_error,
                         req_headers=WebApi._get_headers())
        
class LoginScreen(Screen):
    def login(self):
        UserCred.store_cred(self.login_email.text,
                            self.login_password.text)
        self.manager.current = "posts"

class PostListItem(Button):
    def __init__(self, post, *args, **kwargs):
        super(PostListItem, self).__init__(*args, **kwargs)
        self.post = post

class PostsScreen(Screen):
    def on_enter(self):
        self.posts_list_container.clear_widgets()
        self.load_posts()

    def load_posts(self):

        def set_post_screen_post(instance):
            '''
            Set the post_id of PostScreen
            '''
            self.post_screen.post = instance.post
        
        def populate_posts(req, results):
            for post in results['posts']:
                body = PostListItem(post, text=post['body'][:40])
                body.bind(on_press=set_post_screen_post)
                self.posts_list_container.add_widget(body)

        def show_login_screen(req, results):
            self.manager.current = "login"

        WebApi.posts(populate_posts,
                     show_login_screen,
                     show_login_screen)

class PostScreen(Screen):
    post = ObjectProperty(0)

    def on_post(self, instance, value):
        '''
        When the post object changes, load that post into the screen
        '''
        # Set the current screen to the post screen
        self.manager.current = "post"

        if self.post['img_url']:
            img_widget = AsyncImage(source=self.post['img_url'])
        else:
            img_widget = Label(text='No Photo Available')
        self.post_details_container.add_widget(img_widget)

        body = Label(text=self.post['body'])
        self.post_details_container.add_widget(body)
        
class PhotoAppScreenManager(ScreenManager):
    pass

class PhotoApp(App):
    def build(self):
        return PhotoAppScreenManager()


if __name__ == '__main__':
    PhotoApp().run()
