"""
******************************************************************************************************
 Project           Eurobot 2015
 Filename          main.py

 Institution:      University of applied Science Bern

 IDE               PyCharm 4.0.3 Build #PY-139.781
 Python            Python 3.4.1

 @author           Yves Jegge und Joel Baertschi
 @date             04.01.2015
 @version          1.0.0

 @copyright        Copyright 2015, Eurobot
 @status           Development

******************************************************************************************************
"""
"""
-----------------------------------------------------------------------------------------------------
Main Programm
-----------------------------------------------------------------------------------------------------
This File will controll the whole GUI programm
-----------------------------------------------------------------------------------------------------
"""
# Import Librarys #
import sys
import threading
import time
from PyQt4 import QtCore, QtGui


# Import Modul #
import GUI.GUI


"""
/*----------------------------------------------------------------------------------------------------
Method: def main(args)
------------------------------------------------------------------------------------------------------
This Method controlls the whole Programm
-----------------------------------------------------------------------------------------------------
Input  Parameter:       sys.argv
Output Parameter:       -
----------------------------------------------------------------------------------------------------*/
"""
def main(args):
    """ The main function starts the gui """
    app = QtGui.QApplication(args)
    GUI_window = GUI.GUI.Ui_MainWindow()
    GUI_window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)
