__author__ = 'mw'

from PyQt4 import QtGui, QtCore
import sys


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtGui.QLabel('Test')
        pixmap = QtGui.QPixmap("./gui/Table.png")
        scaledpixmap = pixmap.scaled(self.label.size(), QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(scaledpixmap)
        #self.label.setScaledContents(True)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addStretch()
        self.setLayout(vbox)


class GameField2(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtGui.QLabel('Test')
        self.pixmap = QtGui.QPixmap("./Table.png")
        scaledpixmap = self.pixmap.scaled(self.label.size(), QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(scaledpixmap)
        #self.label.setScaledContents(True)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addStretch()
        self.setLayout(vbox)

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        painter.end()


class GameField3(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QtGui.QPixmap("./Table.png")

    def paintEvent(self, event):
        widget_height = self.size().height()
        widget_width = self.size().width()
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.drawPixmap(0, 0, widget_width, widget_height, self.pixmap)
        painter.end()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    can_window = GameField3()
    can_window.show()
    sys.exit(app.exec_())
