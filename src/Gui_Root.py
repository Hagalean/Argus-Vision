from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from counter import Counter
from Login_manager import Login_Manager

import cv2
from functools import partial


from kivy.config import Config
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'width', '1100')
Config.set('graphics', 'height', '800')

from kivy.core.window import Window
Window.clearcolor = (1, 1, 1, 1)

Builder.load_file("Gui_root.kv")

class SignInScreen(Screen):

    def __init__(self, **kwargs):
        super(SignInScreen, self).__init__(**kwargs)

        title_label = Label(text="Argus Vision", markup=True)
        title_label.pos = (492, 600)
        title_label.size_hint = (None, None)
        title_label.font_size = (40)
        title_label.color = (0, 0, 0, 1)


        email_input = TextInput(hint_text='Email Address')
        email_input.focus = True
        email_input.write_tab = False
        email_input.multiline = False
        email_input.pos = (410, 450)
        email_input.size_hint = (None, None)
        email_input.size = (280, 30)
        self.email_input = email_input

        password_input = TextInput(hint_text='Password')
        password_input.password = True
        password_input.write_tab = False
        password_input.multiline = False
        password_input.pos = (410, 390)
        password_input.size_hint = (None, None)
        password_input.size = (280, 30)
        self.password_input = password_input

        login_button = Button(text="Login")
        login_button.background_color = (0.4, 0.5, 0.6, 1)
        login_button.pos =(450, 250)
        login_button.size_hint = (None, None)
        login_button.size = (200, 50)

        signup_button = Button(text="Sign Up")
        signup_button.background_color = (0.4, 0.5, 0.6, 1)
        signup_button.pos = (450, 180)
        signup_button.size_hint = (None, None)
        signup_button.size = (200, 50)

        forgot_pw = Label(text="[ref=][color=0000ff]Forgot your password?[/color][/ref]", markup=True)
        forgot_pw.pos = (500, 100)
        forgot_pw.size_hint = (None, None)
        forgot_pw.font_size = (16)
        forgot_pw.color = (0, 0, 0, 1)
        self.forgot_pw_text = ""

        signup_button.bind(on_release=self.go_signup)
        forgot_pw.bind(on_ref_press=self.forgot_pw)
        login_button.bind(on_release=self.login ) # partial(self.login,email_input.text,password_input.text))
        Window.bind(on_key_down=self.key_press)

        self.add_widget(title_label)
        self.add_widget(email_input)
        self.add_widget(password_input)
        self.add_widget(login_button)
        self.add_widget(forgot_pw)
        self.add_widget(signup_button)

    def forgot_pw(self, instance, value):

        self.Popuplayout = FloatLayout()
        email_input = TextInput(hint_text='Enter Your Email Address')

        email_input.focus = True
        email_input.write_tab = False
        email_input.multiline = False
        email_input.pos = (410, 450)
        email_input.size_hint = (None, None)
        email_input.size = (280, 40)
        self.forgot_pw_text = email_input


        closeButton = Button(text="Exit")
        closeButton.size_hint = (None, None)
        closeButton.size = (200, 40)
        closeButton.pos = (450, 250)

        submit_button = Button(text="Request Password Reset")
        submit_button.size_hint = (None, None)
        submit_button.size = (200, 40)
        submit_button.pos = (450, 320)
        submit_button.bind(on_release=self.pw_reset)

        self.Popuplayout.add_widget(submit_button)
        self.Popuplayout.add_widget(closeButton)
        self.Popuplayout.add_widget(email_input)

        self.popup = Popup(title='Forgot Your Password?',title_color=(0,0,0,1),
                      content=self.Popuplayout, size_hint=(None, None), size=(400, 400), background=("white"))
        self.popup.open()

        closeButton.bind(on_release=self.popup.dismiss)
        submit_button.bind(on_release=self.pw_reset)

    def login(self, button):
        email = self.email_input.text
        pw = self.password_input.text
        lg = App.get_running_app().login_manager.check_credentials(email, pw)
        if lg:
            self.manager.current = 'CamSelect'
        else:
            wrong_cred = Label(text="Incorrect email or password", markup=True)
            wrong_cred.pos = (498, 300)
            wrong_cred.size_hint = (None, None)
            wrong_cred.font_size = (16)
            wrong_cred.color = (1, 0, 0, 1)
            self.add_widget(wrong_cred)
        pass

    def key_press(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40 and self.manager.current == 'SignIn':
            self.login("")

    def pw_reset(self, button):

        email = self.forgot_pw_text.text
        success = App.get_running_app().login_manager.password_reset_reqquest(email)

        if success:
            email_sent = Label(text="You will receive an email soon ", markup=True)
            email_sent.pos = (498, 350)
            email_sent.size_hint = (None, None)
            email_sent.font_size = (16)
            email_sent.color = (0, 0, 1, 1)
            self.Popuplayout.add_widget(email_sent)

    def go_signup(self, button):
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'SignUp'

class SignUpScreen(Screen):
    def __init__(self, **kwargs):
        super(SignUpScreen, self).__init__(**kwargs)

        title_label = Label(text="Create Account", markup=True)
        title_label.pos = (492, 700)
        title_label.size_hint = (None, None)
        title_label.font_size = (40)
        title_label.color = (0, 0, 0, 1)

        email_input = TextInput(hint_text='Email Address')
        email_input.focus = True
        email_input.write_tab = False
        email_input.multiline = False
        email_input.pos = (410, 650)
        email_input.size_hint = (None, None)
        email_input.size = (280, 30)
        self.email_input = email_input

        password_input = TextInput(hint_text='Password')
        password_input.password = True
        password_input.write_tab = False
        password_input.multiline = False
        password_input.pos = (410, 590)
        password_input.size_hint = (None, None)
        password_input.size = (280, 30)
        self.password_input = password_input

        re_password_input = TextInput(hint_text='Re-Enter Password')
        re_password_input.password = True
        re_password_input.write_tab = False
        re_password_input.multiline = False
        re_password_input.pos = (410, 530)
        re_password_input.size_hint = (None, None)
        re_password_input.size = (280, 30)
        self.re_password_input = re_password_input

        name_input = TextInput(hint_text='Name')
        name_input.write_tab = False
        name_input.multiline = False
        name_input.pos = (410, 470)
        name_input.size_hint = (None, None)
        name_input.size = (280, 30)
        self.name_input = name_input

        surname_input = TextInput(hint_text='Surname')
        surname_input.write_tab = False
        surname_input.multiline = False
        surname_input.pos = (410, 410)
        surname_input.size_hint = (None, None)
        surname_input.size = (280, 30)
        self.surname_input = surname_input

        phone_input = TextInput(hint_text='Phone number')
        phone_input.write_tab = False
        phone_input.multiline = False
        phone_input.pos = (410, 350)
        phone_input.size_hint = (None, None)
        phone_input.size = (280, 30)
        self.phone_input = phone_input

        birthdate_input = TextInput(hint_text='Birthday, DD/MM/YYYY')
        birthdate_input.write_tab = False
        birthdate_input.multiline = False
        birthdate_input.pos = (410, 290)
        birthdate_input.size_hint = (None, None)
        birthdate_input.size = (280, 30)
        self.birthdate_input = birthdate_input

        create_account_button = Button(text="Create Account")
        create_account_button.background_color = (0.4, 0.5, 0.6, 1)
        create_account_button.pos = (450, 200)
        create_account_button.size_hint = (None, None)
        create_account_button.size = (200, 50)
        create_account_button.bind(on_release=self.create_account)

        return_to_login_button = Button(text="Return to Login page")
        return_to_login_button.background_color = (0.4, 0.5, 0.6, 1)
        return_to_login_button.pos = (450, 120)
        return_to_login_button.size_hint = (None, None)
        return_to_login_button.size = (200, 50)
        return_to_login_button.bind(on_release=self.return_to_login)

        self.alert_label = Label()

        self.add_widget(title_label)
        self.add_widget(self.email_input)
        self.add_widget(self.password_input)
        self.add_widget(self.re_password_input)
        self.add_widget(self.name_input)
        self.add_widget(self.surname_input)
        self.add_widget(self.phone_input)
        self.add_widget(self.birthdate_input)
        self.add_widget(create_account_button)
        self.add_widget(return_to_login_button)

    def return_to_login(self, button):
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'SignIn'

    def create_account(self, button):
        email = self.email_input.text
        pw = self.password_input.text
        rpw = self.re_password_input.text
        name = self.name_input.text
        surname = self.surname_input.text
        phone = self.phone_input.text
        bday = self.birthdate_input.text

        if email == "" or pw == "" or rpw == "" or name == "" or surname == "" or phone == "" or bday == "":
            self.remove_widget(self.alert_label)
            self.alert_label = Label(text="Please fill all fields", markup=True)
            self.alert_label.pos = (498, 220)
            self.alert_label.size_hint = (None, None)
            self.alert_label.font_size = (16)
            self.alert_label.color = (1, 0, 0, 1)
            self.add_widget(self.alert_label)
            return

        if pw != rpw:
            self.remove_widget(self.alert_label)
            self.alert_label = Label(text="Passwords does not match", markup=True)
            self.alert_label.pos = (498, 220)
            self.alert_label.size_hint = (None, None)
            self.alert_label.font_size = (16)
            self.alert_label.color = (1, 0, 0, 1)
            self.add_widget(self.alert_label)
            return

        success = App.get_running_app().login_manager.create_account(email, pw, name, surname, phone, bday)

        if success:
            self.remove_widget(self.alert_label)
            self.alert_label = Label(text="Account created successfully, now you can login", markup=True)
            self.alert_label.pos = (498, 220)
            self.alert_label.size_hint = (None, None)
            self.alert_label.font_size = (16)
            self.alert_label.color = (0, 0, 1, 1)
            self.add_widget(self.alert_label)
        else:
            self.remove_widget(self.alert_label)
            self.alert_label = Label(text="An error occured while creating your account", markup=True)
            self.alert_label.pos = (498, 220)
            self.alert_label.size_hint = (None, None)
            self.alert_label.font_size = (16)
            self.alert_label.color = (1, 0, 0, 1)
            self.add_widget(self.alert_label)




class CameraSelectionScreen(Screen):

    def set_vs(self):
        videoInput = "videos/example_01.mp4"
        self.manager.add_widget(CameraStreamScreen(cv2.VideoCapture(videoInput), name='Stream'))

class CameraStreamScreen(Screen):
    def __init__(self,vs, **kwargs):
        super(CameraStreamScreen, self).__init__(**kwargs)

        print("called")
        stream = VideoStream(vs)
        stream.size_hint = (None,None)
        stream.pos = (50, 100)
        stream.size = (1000,700)
        self.add_widget(stream)

    def delete_screen(self):
        self.manager.remove_widget(self)

class DrawLineScreen(Screen):
    pass

class EditLineScreen(Screen):
    pass

class StatisticsScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class VideoStream(Image):
    def __init__(self,vs, **kwargs):
        super(VideoStream, self).__init__(**kwargs)
        self.vs = vs
        Clock.schedule_interval(self.update, 0.01)

    def update(self, dt):
        # frame = vs.read()[1]

        if self.vs is not None:
            frame = App.get_running_app().program.loop_function()
            frame = cv2.resize(frame,(1000,700))
            if True:
                # convert it to texture
                buf1 = cv2.flip(frame, 0)
                buf = buf1.tostring()
                image_texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                # display image from the texture
                self.texture = image_texture



class App_root(App):
    def __init__(self, **kwargs):
        super(App_root, self).__init__(**kwargs)
        self.program = Counter()
        self.login_manager = Login_Manager()


    def build(self):
        sm = ScreenManager()

        sm.add_widget(SignInScreen(name='SignIn'))
        sm.add_widget(SignUpScreen(name='SignUp'))
        sm.add_widget(CameraSelectionScreen(name='CamSelect'))
        sm.add_widget(DrawLineScreen(name='DrawLine'))
        sm.add_widget(EditLineScreen(name='EditLine'))
        sm.add_widget(StatisticsScreen(name='Statistics'))
        sm.add_widget(SettingsScreen(name='Settings'))

        return sm

if __name__ == '__main__':
    App_root(title="Argus Vision").run()

