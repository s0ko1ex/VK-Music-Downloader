import npyscreen, logics, widgets, threading, sys

downloader = logics.VkDownloader()
        
def captcha_handler(captcha):
    CaptchaForm = CenterForm.getClassCopy()
    CaptchaForm.set_dimensions(70, 7)
    formHandler = CaptchaForm(name="Captcha", color="STANDOUT")

    formHandler.mUrl = formHandler.add_widget(npyscreen.TitleFixedText, name = "Url", value = captcha.get_url())
    formHandler.mKey = formHandler.add_widget(npyscreen.TitleText, name = "Key")
    formHandler.add_button(npyscreen.MiniButtonPress, "OK", -8, -2, formHandler.exit_editing)

    file = open("captcha.jpg", "wb")
    file.write(captcha.get_image())
    file.close()

    formHandler.edit()
    
    return captcha.try_again(key = formHandler.mKey.value)

class VkDownloaderApp(npyscreen.StandardApp):
    def onStart(self):
        self.addForm("MAIN", LoginForm, name = "Login")
        self.addFormClass("MAIN_SCREEN", MainForm, name = "VK Music Downloader")
    
    def change_form(self, name):
        self.switchForm(name)
        self.resetHistory()

class CenterForm(npyscreen.FormBaseNew):
    @staticmethod
    def getClassCopy():
        class B(__class__):
            pass
        return B
    
    @staticmethod
    def set_dimensions(x, y):
        __class__.DEFAULT_COLUMNS = x
        __class__.DEFAULT_LINES = y

    def create(self):
        self.center_on_display()

    def resize(self):
        npyscreen.blank_terminal()
        self.center_on_display()
    
    def add_button(self, btn_class, btn_name, btn_relx, btn_rely, btn_action=None):
        self.add_widget(btn_class,
                        name=btn_name,
                        relx=btn_relx,
                        rely=btn_rely,
                        when_pressed_function=btn_action,
                        use_max_space=True)

class LoginForm(npyscreen.ActionFormV2):
    DEFAULT_LINES = 7
    DEFAULT_COLUMNS = 50

    def create(self):
        self.center_on_display()

        self.mLogin = self.add_widget(npyscreen.TitleText, name = "Login")
        self.mPassword = self.add_widget(npyscreen.TitlePassword, name = "Password")
    
    def resize(self):
        npyscreen.blank_terminal()
        self.center_on_display()
    
    def on_cancel(self):
        sys.exit(0)
    
    def on_ok(self):
        if downloader.login(self.mLogin.value, self.mPassword.value, captcha_handler=captcha_handler):
            self.parentApp.change_form("MAIN_SCREEN")
        else:
            string = "Wrong credentials!"
            VkNotifier = CenterForm.getClassCopy()
            VkNotifier.set_dimensions(40, 5)
            vk_notifier = VkNotifier(name = "VK", color = "STANDOUT")
            vk_notifier.message = vk_notifier.add_widget(npyscreen.FixedText, relx = 20 - len(string)//2, editable = False, value = string)
            vk_notifier.okButton = vk_notifier.add_button(npyscreen.MiniButtonPress, "OK", -8, -2, vk_notifier.exit_editing)
            vk_notifier.edit()

def wait_until(width = 40, height = 5):
    string = "Loading..."
    WaitForm = CenterForm.getClassCopy()
    WaitForm.set_dimensions(width, height)

    values = ['\n' for _ in '_'*(height - 4)]
    values[len(values)//2] = string
    values = "".join(values)

    wait_form = WaitForm(name = "Wait")
    wait_form.text = wait_form.add_widget(npyscreen.FixedText, value = values, relx = 20 - len(string)//2, max_height = len(values))
    
    return wait_form

class MainForm(npyscreen.FormBaseNew):
    def create(self):
        def download():
            mode, condition, songs = self.mMode.value, "True", self.cur_songs
            
            def start():
                self.downloadButton.editable = False

            def end():
                self.mMulty.values = ("Done!", )
                self.downloadButton.editable = True
                self.display()
            
            def while_func(message):
                self.mMulty.values = message
                self.mMulty.display()

            if 1 in mode:
                condition = self.mCondition.value
            if 0 in mode:
                songs = [self.cur_songs[i] for i in self.mSongs.value]
            
            self.mMulty.values = self.mSongs.value
            downloader.download(songs, folder = "./%s/"%self.mFolder.value, condition = condition, overrite = 2 in mode, start_func=start, end_func=end, while_func=while_func)
        
        move = 3
        self.mSide = self.add_widget(widgets.SideSelector, name = "Albums", max_width = 30,  rely = 1)
        self.mSongs = self.add_widget(widgets.SongSelector, name = "Songs", relx = 32, rely = 1, max_height =  -8 - move)

        self.mSettingsTitle = self.add_widget(npyscreen.FixedText, value = "Download Settings", relx = 34, rely = - 10 - move, color = "CURSOR", editable = False)
        self.mMode = self.add_widget(npyscreen.TitleMultiSelect, name = "Mode", values = ["Selected", "Matching condition", "Overrite"], value = [0,2], relx = 34, rely = -8 - move, max_height=4, max_width=42)
        self.mFolder = self.add_widget(npyscreen.TitleText, name = "Folder", relx = 34, rely = -4 - move, max_width = 34, value = "VK Music")
        self.mCondition = self.add_widget(npyscreen.TitleText, name = "Condition", relx = 68, rely = -4 - move)
        self.mMulty = self.add_widget(npyscreen.TitleMultiLine, name = "Actions", values = ["Here information on all", "actions will be placed."], relx = 34, rely = -2 - move, max_height = 2, editable = False, scroll_exit = True)

        self.downloadButton = self.add_widget(npyscreen.MiniButtonPress, name = "Download", rely = -2, relx = -22, use_max_space = True, when_pressed_function = download)
        self.exitButton = self.add_widget(widgets.ExitButton, name = "Exit", rely = -2, relx = -10, use_max_space = True)
        
        self.cur_songs = []

        self.add_event_hander("event_album_selected", self.select_album)

        self.initAlbums()

    def initAlbums(self):
        self_i = self

        class AlbumThread(threading.Thread):
            def run(self):
                albums = ["All", *map(lambda a: a['title'], downloader.get_albums())]
                self_i.mSide.values = albums
                self_i.mSide.display()
        
        AlbumThread().start()
    
    def select_album(self, event):
        if event.payload == [0]:
            self.initSongs()
        else:
            self.initAlbum(event.payload[0] - 1)
        
    def initAlbum(self, album_number):
        self_i = self
        edit, exit_editing = (lambda a: (a.edit, a.exit_editing))(wait_until())

        class SongThread(threading.Thread):
            def run(self):
                self_i.cur_songs = downloader.get_album(album_number)
                songs = ["%s - %s"%(a['artist'], a['title']) for a in self_i.cur_songs]
                self_i.mSongs.values = songs
                self_i.mSongs.value = []
                self_i.mSongs.display()
                exit_editing()
        
        SongThread().start()
        edit()
    
    def initSongs(self):
        self_i = self
        edit, exit_editing = (lambda a: (a.edit, a.exit_editing))(wait_until())

        class SongThread(threading.Thread):
            def run(self):
                self_i.cur_songs = downloader.get_tracks()
                songs = ["%s - %s"%(a['artist'], a['title']) for a in self_i.cur_songs]
                self_i.mSongs.values = songs
                self_i.mSongs.value = []
                self_i.mSongs.display()
                exit_editing()
        
        SongThread().start()
        edit()

VkDownloaderApp().run()