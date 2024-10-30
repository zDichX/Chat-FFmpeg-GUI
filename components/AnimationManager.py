
from PySide6.QtWidgets import QApplication, QGraphicsOpacityEffect, QWidget
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QPoint

import math

class AnimationManager:
    def __init__(self, widget: QWidget):
        self.widget = widget
        self.timer = None
        self.t = 0
        self.step = 0
        
    def start_animation(self):
        widget = self.widget
        self.pos_animation = QPropertyAnimation(widget, b"pos")
        self.pos_animation.setDuration(1000)
        self.pos_animation.setStartValue(widget.pos())
        self.pos_animation.setEndValue(QPoint(widget.pos().x(), widget.pos().y() + 100))
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.pos_animation.start()
        
    def click_animation(self, button):
        # 创建 QGraphicsOpacityEffect 对象并设置到按钮上
        opacity_effect = QGraphicsOpacityEffect(button)
        button.setGraphicsEffect(opacity_effect)

        # 创建 QPropertyAnimation 对象，用于动画效果
        self.clk_animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.clk_animation.setDuration(200)
        self.clk_animation.setStartValue(1)
        self.clk_animation.setEndValue(0.7)
        self.clk_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 开始动画
        self.clk_animation.start()

    def move_to_center(self):
        widget = self.widget
        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(widget.width() // 2, widget.height() // 2)
        self.mov_animation = QPropertyAnimation(widget, b"pos")
        self.mov_animation.setDuration(600)
        self.mov_animation.setStartValue(widget.pos())
        self.mov_animation.setEndValue(QPoint(self.screen_center.x() - self.window_center.x(), self.screen_center.y() - self.window_center.y() - 100))
        self.mov_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.mov_animation.finished.connect(self.processing_animation)
        self.mov_animation.start()

    def processing_animation(self):
        widget = self.widget
        self.timer = QTimer(widget)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # 60 FPS

        self.screen_center = self.get_screen_center()
        self.window_center = QPoint(widget.width() // 2, widget.height() // 2)
        self.t = 0
        self.step = 0

    def get_screen_center(self):
        screen = QApplication.primaryScreen().geometry()
        return QPoint(screen.width() // 2, screen.height() // 2)

    def update_position(self):
        radius = 100
        if self.step >= 0:
            self.t += self.step
            if self.t <= 10000:
                self.step += (0.5 - self.progress) / 300
        else:
            self.timer.stop()
            return
        
        angle = self.t - math.pi / 2
        x = int(self.screen_center.x() + radius * math.cos(angle) - self.window_center.x())
        y = int(self.screen_center.y() + radius * math.sin(angle) - self.window_center.y())
        self.widget.move(x, y)

    def delayed_animation_start(self):
        delay = 0
        QTimer.singleShot(delay, self.start_animation)
