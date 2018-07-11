import vk_api, os, requests, re, threading
from vk_api.audio import VkAudio
from jconfig.memory import MemoryConfig

def matches(regex, string):
    return bool(re.findall(regex, string))

class VkDownloader():
    def __init__(self):
        self._session : vk_api.VkApi = None
        self._audio : VkAudio = None
        self._cache: list = []
        self._albums: list = []

    def login(self, username, password, exception_handler = None, bad_password_handler = None, success_handler = None, captcha_handler = None):
        self._session = vk_api.VkApi(username, password, config=MemoryConfig, captcha_handler=captcha_handler)

        try:
            self._session.auth()
        except vk_api.BadPassword:
            if bad_password_handler:
                bad_password_handler()
            return False
        except Exception:
            if exception_handler:
                exception_handler()
            return False
        
        self._audio = VkAudio(self._session)
        return True


    def get_tracks(self):
        if self._audio and not self._cache:
            self._cache = self._audio.get()
        return self._cache

    def get_albums(self):
        if self._audio and not self._albums:
            self._albums = self._audio.get_albums()
        return self._albums

    def get_album(self, album_number):
        return self._audio.get(album_id=self._albums[album_number]['id'])

    def refresh(self):
        self._cache = self._audio.get()
        self._albums = self._audio.get_albums()

    def download(self, songs, folder, condition = "True", overrite = False, start_func = None, end_func = None, while_func = None):        
        class DownloadThread(threading.Thread):
            def run(self):                
                if not os.path.exists(folder):
                    while_func(("Creating folder...",))
                    os.makedirs(folder)
                
                try:
                    eval(condition)
                except Exception:
                    if(while_func):
                        while_func(("Invalid condition!",))
                    if(end_func):
                        end_func()
                    return

                while_func(("Starting download...",))
                
                for i in songs:
                    name = "%s - %s"%(i['artist'], i['title'])

                    if (eval(condition) or (condition == None)):
                        song = requests.get(i['url'], stream = True)
                        size = int(song.headers['Content-Length'])

                        i = 0
                        if os.path.exists(folder+name+".mp3") and not overrite:
                            while_func(("Downloading %s..."%name , "File already downloaded."))
                            continue
                        file = open(folder+name+".mp3", "wb")

                        for chunk in song.iter_content(chunk_size = 1024):
                            if chunk:
                                i += 1
                                file.write(chunk)
                            if while_func:
                                while_func(("Downloading %s..."%name , "Downloaded %d"%(i*1024*100//size)+r'%'))
                        
                        file.close()
                if end_func:
                    end_func()
        
        DownloadThread().start()

        if start_func:
            start_func()