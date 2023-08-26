from vlc import Instance
import os

class RemoteVlc():
    def __init__(self):
        self.Player = Instance('--loop')

    def addPlaylist(self, path):
        self.mediaList = self.Player.media_list_new()
        #path = r"C:\Users\dell5567\Desktop\engsong"
        # songs = os.listdir(path)
        # for s in songs:
        #     self.mediaList.add_media(self.Player.media_new(os.path.join(path,s)))
        self.mediaList.add_media(self.Player.media_new(path))
        self.listPlayer = self.Player.media_list_player_new()
        self.listPlayer.set_media_list(self.mediaList)
        self.listPlayer.play()
    def play(self):
        self.listPlayer.play()
    def next(self):
        self.listPlayer.next()
    def pause(self):
        self.listPlayer.pause()
    def previous(self):
        self.listPlayer.previous()
    def stop(self):
        self.listPlayer.stop()
    def goto(self, index):
        print(self.mediaList.item_at_index(int(index)))
        print(self.listPlayer.play_item_at_index(index))

