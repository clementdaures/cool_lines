from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *


class CoolCheckbox(QCheckBox):
    def __init__(self, *args, **kwargs):
        QCheckBox.__init__(self, *args, **kwargs)

        self._circle_position_x = 3
        self._background_color = QColor(255,0,0)
        #Creating ellipse animation:
        self.ellipse_animation = QPropertyAnimation(self, b"circle_position")


        #Creating color animation:
        self.background_color_animation = QPropertyAnimation(self, b"background_color")


        self.stateChanged.connect(self.toggleCheckbox)
        

        self.value = None


        


    #Create new circle position property:
    @Property(float) #Getter
    def circle_position(self):
        return self._circle_position_x
    
    @circle_position.setter
    def circle_position(self, pos):
        self._circle_position_x = pos
        self.update()


    #Create new background color property:
    @Property(QColor) #Getter
    def background_color(self):
        return self._background_color
    
    @background_color.setter
    def background_color(self, color):
        self._background_color = color
        self.update()
    


    def setupAnimations(self, start_checked = False,
                        animation_duration = 200,
                        animation_curve = QEasingCurve.OutQuart,
                        circle_height_border = 15,
                        circle_pos_y = 3,
                        checked_color = QColor(0,255,0),
                        unchecked_color = QColor(255,0,0) ):
        
        self.animation_duration = animation_duration
        self.ellipse_animation.setDuration(animation_duration)
        self.ellipse_animation.setEasingCurve(animation_curve)

        self.circle_position_y = circle_pos_y

        #Color:
        self.background_color_animation.setDuration(animation_duration)


        self.background_color_animation.setStartValue(checked_color)
        self.background_color_animation.setEndValue(unchecked_color)

        if start_checked:
            self.setChecked(True)
            self._background_color = checked_color



    def paintEvent(self, event):

        '''super().paintEvent(event)'''

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen()
        pen.setColor(QColor(0,0,0,0))
        painter.setPen(pen)

        
        
        #Draw Checkbox background
        rect = QRect(0,0, self.width(), self.height())
        painter.setBrush(self._background_color)
        painter.drawRoundedRect(0,0, rect.width(), self.height(), (self.height()/2), (self.height()/2))

        

        painter.setBrush(QColor(255,255,255))
        #Calculating the height of the circle:
        self.circle_height = (self.height() - (self.circle_position_y*2))
        painter.drawEllipse(QRectF(self._circle_position_x, self.circle_position_y, self.circle_height, self.circle_height))



        painter.end()
        


    #Set new hitbox:
    def hitButton(self, pos: QPoint):
        return self.contentsRect().contains(pos)
    
    def startTransition(self):

        current_state = self.isChecked()

        self.ellipse_animation.setCurrentTime(self.animation_duration)
        self.ellipse_animation.stop()

        self.background_color_animation.setCurrentTime(self.animation_duration)
        self.background_color_animation.stop()


        self.ellipse_animation.setEndValue((self.width() - self.circle_height) - self._circle_position_x)
        self.ellipse_animation.start()

        if current_state :
            self.background_color_animation.setDirection(self.background_color_animation.Backward)
        else:
            self.background_color_animation.setDirection(self.background_color_animation.Forward)
        self.background_color_animation.start()

    

    def toggleCheckbox(self):
        try:
            self.startTransition()
        except:
            pass