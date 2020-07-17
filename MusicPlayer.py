from PyQt5.QtGui import *

from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *

from PyQt5.QtCore import *

from tinytag import TinyTag
import shutil

import os
import sys


from player import Ui_MainWindow





class PlayListModel(QAbstractListModel):
    def __init__(self,playlist):
        super(PlayListModel, self).__init__()
        self.playlist=playlist

    def data(self, index, role):
            if role == Qt.DisplayRole:
                media = self.playlist.media(index.row())
                return media.canonicalUrl().fileName()

    def rowCount(self, index):
            return self.playlist.mediaCount()



class MusicPlayer(QMainWindow,Ui_MainWindow):
    def __init__(self,*args, **kwargs):
        super(MusicPlayer, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.player=QMediaPlayer()
        self.speed=0
        self.lblspeed.setText(str(self.speed))

        self.playlist=QMediaPlaylist()
        self.player.setPlaylist(self.playlist)


        self.btn_play.clicked.connect(lambda :self.player.play())
        self.btn_pause.clicked.connect(lambda :self.player.pause())
        self.btn_stop.clicked.connect(lambda :self.player.stop())
        self.btn_next.clicked.connect(lambda :self.playlist.next())
        self.btn_prev.clicked.connect(lambda :self.playlist.previous())




        self.volumeSlider.setValue(100)
        self.volumeSlider.valueChanged.connect(self.player.setVolume)


        self.model=PlayListModel(self.playlist)
        self.musicList.setModel(self.model)
        self.playlist.currentIndexChanged.connect(self.playlist_position_changed)
        selectionModel=self.musicList.selectionModel()
        selectionModel.selectionChanged.connect(self.playlist_selection_changed)

        self.player.durationChanged.connect(self.update_duration)
        self.player.positionChanged.connect(self.update_position)
        self.slider_play.valueChanged.connect(self.player.setPosition)



        self.btn_addsong.clicked.connect(self.Addmusic)

        self.btn_delsong.clicked.connect(self.RemoveMusic)
        self.ReadFolderMusic()


        self.playmode='shuffle'
        self.lbl_playmode.setText(self.playmode)

        self.btn_shuffle.clicked.connect(self.setShuffleMode)
        self.btn_repeat.clicked.connect(self.setRepeatMode)
        self.btn_incSpeed.clicked.connect(self.IncreaseSpeedMusic)
        self.btn_decSpeed.clicked.connect(self.DeceaseSpeedMusic)

    def playlist_selection_changed(self, ix):
        self.player.stop()
        i = ix.indexes()[0].row()
        self.playlist.setCurrentIndex(i)
        m=self.playlist.media(i)
        m=QMediaContent.canonicalUrl(m).path().title()
        if m[0]=='/':
            m=m[1:]

        print(m)
        infoMusic=TinyTag.get(m,image=True)
        img=infoMusic.get_image()

        if os.path.exists('imgMusic.jpg'):
             os.remove('imgMusic.jpg')

        imgfile='imgMusic.jpg'
        if img:
             img[:20]
             with open(imgfile,'wb') as img_file:
                 img_file.write(img)
                 pixel = QPixmap(imgfile)
                 self.lblimage.setPixmap(pixel)

        self.lblsong.setText(infoMusic.title)
        self.lblalbum.setText(infoMusic.album)
        self.lblartist.setText(infoMusic.artist)
        self.lbl_namemusic.setText(infoMusic.title)

        self.model.layoutChanged.emit()

    # def dragEnterEvent(self, e):
    #     if e.mimeData().hasUrls():
    #         e.acceptProposedAction()
    #
    # def dropEvent(self, e):
    #     for url in e.mimeData().urls():
    #         self.playlist.addMedia(
    #             QMediaContent(url)
    #         )






    def playlist_position_changed(self, i):
        if i > -1:
            ix = self.model.index(i)
            self.index2=i
            self.musicList.setCurrentIndex(ix)



    def update_duration(self,duration):
        self.slider_play.setMaximum(duration)
        if duration>=0:
            self.lblfulltime.setText(self.ConvertToTime(duration))


    def update_position(self,position):
        if position>= 0:
            self.lbltimeplay.setText(self.ConvertToTime(position))

        self.slider_play.blockSignals(True)
        self.slider_play.setValue(position)
        self.slider_play.blockSignals(False)


    def ConvertToTime(self,ms):
        # s = 1000
        # m = 60000
        # h = 360000
        h, r = divmod(ms, 36000)
        m, r = divmod(r, 60000)
        s, _ = divmod(r, 1000)
        return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))


    def Addmusic(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",  "mp3 Audio (*.mp3)")
        if path:
            src = 'music/' + os.path.basename(path)
            shutil.copyfile(path,src)
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(src)))
            self.model.layoutChanged.emit()



    def RemoveMusic(self):
        self.playlist.setCurrentIndex(self.index2)
        select_music = self.playlist.media(self.index2)
        path_music_selected = QMediaContent.canonicalUrl(select_music).path().title()
        if os.path.exists(path_music_selected[1:]):
            os.remove(path_music_selected[1:])
            self.playlist.removeMedia(self.index2)

        self.model.layoutChanged.emit()



    def ReadFolderMusic(self):
        root='music/'
        with os.scandir(root) as lst:
            for f in lst:
                if os.path.isfile(f):
                    music_path=os.path.abspath(f)

                    self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(music_path)))

        self.model.layoutChanged.emit()

    def setShuffleMode(self):
        self.playmode='shuffle'
        self.lbl_playmode.setText(self.playmode)
        self.playlist.shuffle()

    def setRepeatMode(self):
        self.playmode='Repeat'
        self.lbl_playmode.setText(self.playmode)
        self.playlist.setPlaybackMode(QMediaPlaylist.Loop)

    def IncreaseSpeedMusic(self):
        self.speed=self.speed+1.0
        self.player.setPlaybackRate(self.speed)
        self.lblspeed.setText(str(self.speed))

    def DeceaseSpeedMusic(self):
        if self.speed > 0:
            self.speed=self.speed-1.0
            self.player.setPlaybackRate(self.speed)
            self.lblspeed.setText(str(self.speed))




if __name__ == '__main__':
    app=QApplication([])
    ui=MusicPlayer()
    ui.show()
    app.exec_()

