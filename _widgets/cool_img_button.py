from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from pathlib import Path


class CoolImgButton(QPushButton):
    def __init__(self, img_path:str, btn_size :QSize, img_size :QSize, bg_color :QColor, corner_radius= 10, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)

        self.button_size= btn_size
        self.pixmap= QPixmap(img_path)
        self.corner_radius= corner_radius
        self.img_size= img_size
        self.bg_color= bg_color


    def paintEvent(self, event):
        
        btn_rect= event.rect()
                   
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # painter.setRenderHint(QPainter.SmoothPixmapTransform)

        p_path= QPainterPath()
        p_path.addRoundedRect(btn_rect, self.corner_radius, self.corner_radius)

        # Scale img
        scaled_pixmap = self.pixmap.scaled(
        self.img_size, 
        Qt.KeepAspectRatioByExpanding, 
        Qt.SmoothTransformation
        )
    
        # Center img
        x = btn_rect.x() - (scaled_pixmap.width() - btn_rect.width()) / 2
        y = btn_rect.y() - (scaled_pixmap.height() - btn_rect.height()) / 2

        painter.fillPath(p_path, self.bg_color) # CD6C1B
        painter.drawPixmap(int(x), int(y), scaled_pixmap)


    def sizeHint(self):
        return self.button_size