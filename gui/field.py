__author__ = 'mw'

from PyQt4 import QtGui, QtCore


class GameField(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        self.label = QtGui.QLabel('Test')
        pixmap = QtGui.QPixmap("./gui/Table.png")
        scaledpixmap = pixmap.scaled(self.label.size(), QtCore.Qt.KeepAspectRatio)
        self.label.setPixmap(scaledpixmap)
        self.label.setScaledContents(True)
        vbox = QtGui.QHBoxLayout()
        vbox.addWidget(self.label)
        vbox.addStretch()
        self.setLayout(vbox)