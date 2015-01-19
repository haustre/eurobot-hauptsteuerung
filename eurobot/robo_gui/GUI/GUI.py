"""
******************************************************************************************************
 Project           Eurobot 2015
 Filename          GUI.py

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
# Import Librarys #
import os
import random
import math
import time
from PyQt4 import QtCore, QtGui



# Import Modules #
import Hardware.GPIO
import Debug.Demo


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)
"""
--------------------------------------------------------------------------------------------------
Ui_MainWindow(QtGui.QWidget)
-----------------------------------------------------------------------------------------------------
This Class will manage the Graphical User Interface from the Main Controll of the Eurobot 2015 running
on an Beagel Bone Black.
-----------------------------------------------------------------------------------------------------
"""
class Ui_MainWindow(QtGui.QWidget):
    def __init__(self):

        # Initialize GUI #
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        ######################
        # Initialize Threads #
        ######################
        self.threads = []
        ThreadPollingButtons = Hardware.GPIO.PollingButton(self)
        ThreadChasingLED = Hardware.GPIO.ChasingLED()
        ThreadPrintOutSettings = Debug.Demo.PrintOutSettings(self)      # Only for Demo
        ThreadSetRandomCoordinate = Debug.Demo.SetRandomCoordinate()    # Only for Demo

        self.connect(ThreadPollingButtons, QtCore.SIGNAL('Settings_TeamColor'), self.setTeamColorRadioButton)
        self.connect(ThreadPollingButtons, QtCore.SIGNAL('Settings_Strategy'), self.setStrategyRadioButton)
        self.connect(ThreadPollingButtons, QtCore.SIGNAL('Settings_NumberofEnemy'), self.setNumberofEnemyRadioButton)
        self.connect(ThreadSetRandomCoordinate, QtCore.SIGNAL('Coordinate'), self.setCoordinate)  # Only for Demo

        self.threads.append(ThreadPollingButtons)
        self.threads.append(ThreadChasingLED)
        self.threads.append(ThreadPrintOutSettings)          # Only for Demo
        self.threads.append(ThreadSetRandomCoordinate)       # Only for Demo


        ThreadPrintOutSettings.start()                       # Only for Demo
        ThreadSetRandomCoordinate.start()                    # Only for Demo
        ThreadChasingLED.start()
        ThreadPollingButtons.start()

    """
    /*----------------------------------------------------------------------------------------------------
    Method: def setupUi(self, MainWindow):
    ------------------------------------------------------------------------------------------------------
    This Method setup all GUI-Element
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow
    Output Parameter:       -
    ----------------------------------------------------------------------------------------------------*/
    """
    def setupUi(self, MainWindow):

        # Settings for Main Widget #
        MainWindow.setFixedSize(800, 480)
        self.centralWidget = QtGui.QWidget(MainWindow)

        # Settings for Font #
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setFamily(_fromUtf8("Ubuntu"))

        # Settings for Label GameStrategy #
        self.lblGameStrategy = QtGui.QLabel(self.centralWidget)
        self.lblGameStrategy.setGeometry(QtCore.QRect(80, 150, 180, 23))
        self.lblGameStrategy.setFont(font)

        # Settings for Label NumberofEnemy #
        self.lblNumberofEnemy = QtGui.QLabel(self.centralWidget)
        self.lblNumberofEnemy.setGeometry(QtCore.QRect(80, 110, 180, 23))
        self.lblNumberofEnemy.setFont(font)

        # Settings for Label Color #
        self.lblTeamColor = QtGui.QLabel(self.centralWidget)
        self.lblTeamColor.setGeometry(QtCore.QRect(80, 70, 180, 23))
        self.lblTeamColor.setFont(font)

        # Settings for Label X-Position #
        self.lblXPosition = QtGui.QLabel(self.centralWidget)
        self.lblXPosition.setGeometry(QtCore.QRect(550, 260, 180, 23))
        self.lblXPosition.setFont(font)

        # Settings for Label Y-Position #
        self.lblYPosition = QtGui.QLabel(self.centralWidget)
        self.lblYPosition.setGeometry(QtCore.QRect(550, 290, 180, 23))
        self.lblYPosition.setFont(font)

        # Settings for Label Angel #
        self.lblAngle = QtGui.QLabel(self.centralWidget)
        self.lblAngle.setGeometry(QtCore.QRect(550, 320, 141, 23))
        self.lblAngle.setFont(font)

        # Settings for Radio Button Team Color #
        self.ButtonGroupTeamColor =QtGui.QButtonGroup()
        self.rbTeamColorYellow = QtGui.QRadioButton(self.centralWidget)
        self.rbTeamColorYellow.setGeometry(QtCore.QRect(280, 70, 128, 28))
        self.rbTeamColorYellow.setFont(font)
        self.rbTeamColorYellow.setChecked(True)
        self.ButtonGroupTeamColor.addButton(self.rbTeamColorYellow)
        self.rbTeamColorGreen = QtGui.QRadioButton(self.centralWidget)
        self.rbTeamColorGreen.setGeometry(QtCore.QRect(380, 70, 128, 28))
        self.rbTeamColorGreen.setFont(font)
        self.ButtonGroupTeamColor.addButton(self.rbTeamColorGreen)

        # Settings for Radio Buttons Number of Enemy #
        self.ButtonGroupNumberofEnemy =QtGui.QButtonGroup()
        self.rbNumberofEnemy1 = QtGui.QRadioButton(self.centralWidget)
        self.rbNumberofEnemy1.setGeometry(QtCore.QRect(280, 110, 42, 28))
        self.rbNumberofEnemy1.setFont(font)
        self.rbNumberofEnemy1.setChecked(True)
        self.ButtonGroupNumberofEnemy.addButton(self.rbNumberofEnemy1)
        self.rbNumberofEnemy2 = QtGui.QRadioButton(self.centralWidget)
        self.rbNumberofEnemy2.setGeometry(QtCore.QRect(380, 110, 42, 28))
        self.rbNumberofEnemy2.setFont(font)
        self.ButtonGroupNumberofEnemy.addButton(self.rbNumberofEnemy2)

        # Settings for Radio Buttons Strategy #
        self.ButtonGroupStrategy =QtGui.QButtonGroup()
        self.rbStrategyA = QtGui.QRadioButton(self.centralWidget)
        self.rbStrategyA.setGeometry(QtCore.QRect(280, 150, 45, 28))
        self.rbStrategyA.setFont(font)
        self.rbStrategyA.setChecked(True)
        self.ButtonGroupStrategy.addButton(self.rbStrategyA)
        self.rbStrategyB = QtGui.QRadioButton(self.centralWidget)
        self.rbStrategyB.setGeometry(QtCore.QRect(380, 150, 45, 28))
        self.rbStrategyB.setFont(font)
        self.ButtonGroupStrategy.addButton(self.rbStrategyB)
        self.rbStrategyC = QtGui.QRadioButton(self.centralWidget)
        self.rbStrategyC.setGeometry(QtCore.QRect(480, 150, 45, 28))
        self.rbStrategyC.setFont(font)
        self.ButtonGroupStrategy.addButton(self.rbStrategyC)

        # Settings for LCD-Time #
        self.lcdTime = QtGui.QLCDNumber(self.centralWidget)
        self.lcdTime.setEnabled(True)
        self.lcdTime.setGeometry(QtCore.QRect(540, 20, 251, 181))
        self.lcdTime.setFont(font)
        self.lcdTime.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lcdTime.setFrameShape(QtGui.QFrame.Box)
        self.lcdTime.setFrameShadow(QtGui.QFrame.Raised)
        self.lcdTime.setSmallDecimalPoint(False)
        self.lcdTime.setDigitCount(5)
        self.lcdTime.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcdTime.display("90:00")

        # Settings for Label Time #
        self.lblTime = QtGui.QLabel(self.centralWidget)
        self.lblTime.setGeometry(QtCore.QRect(550, 30, 161, 17))
        font.setPointSize(10)
        self.lblTime.setFont(font)

        # Settings for Label Settings #
        self.lblSettings = QtGui.QLabel(self.centralWidget)
        self.lblSettings.setGeometry(QtCore.QRect(70, 30, 161, 17))
        font.setPointSize(10)
        self.lblSettings.setFont(font)

        # Settings for Label Status Information #
        self.lblStatusInformation = QtGui.QLabel(self.centralWidget)
        self.lblStatusInformation.setGeometry(QtCore.QRect(550, 220, 161, 17))
        font.setPointSize(10)
        self.lblStatusInformation.setFont(font)

        # Settings for Line #
        self.line1 = QtGui.QFrame(self.centralWidget)
        self.line1.setGeometry(QtCore.QRect(50, 20, 20, 180))
        self.line1.setFrameShape(QtGui.QFrame.VLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2 = QtGui.QFrame(self.centralWidget)
        self.line2.setGeometry(QtCore.QRect(520, 20, 20, 180))
        self.line2.setFrameShape(QtGui.QFrame.VLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3 = QtGui.QFrame(self.centralWidget)
        self.line3.setGeometry(QtCore.QRect(60, 10, 471, 20))
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line4 = QtGui.QFrame(self.centralWidget)
        self.line4.setGeometry(QtCore.QRect(60, 190, 471, 20))
        self.line4.setFrameShape(QtGui.QFrame.HLine)
        self.line4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line5 = QtGui.QFrame(self.centralWidget)
        self.line5.setGeometry(QtCore.QRect(530, 210, 20, 261))
        self.line5.setFrameShape(QtGui.QFrame.VLine)
        self.line5.setFrameShadow(QtGui.QFrame.Sunken)
        self.line6 = QtGui.QFrame(self.centralWidget)
        self.line6.setGeometry(QtCore.QRect(540, 200, 251, 20))
        self.line6.setFrameShape(QtGui.QFrame.HLine)
        self.line6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line7 = QtGui.QFrame(self.centralWidget)
        self.line7.setGeometry(QtCore.QRect(780, 210, 20, 261))
        self.line7.setFrameShape(QtGui.QFrame.VLine)
        self.line7.setFrameShadow(QtGui.QFrame.Sunken)
        self.line8 = QtGui.QFrame(self.centralWidget)
        self.line8.setGeometry(QtCore.QRect(540, 460, 251, 20))
        self.line8.setFrameShape(QtGui.QFrame.HLine)
        self.line8.setFrameShadow(QtGui.QFrame.Sunken)

        # Loading Picture Map #
        self.picMap = QtGui.QLabel(MainWindow)
        self.mapLength=390
        self.mapWidth = 260
        self.mapXCoordinate = 100
        self.mapYCoordinate = 202
        self.picMap.setGeometry(self.mapXCoordinate,self.mapYCoordinate,self.mapLength,self.mapWidth)
        self.table_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'Table.png'))
        self.picMap.setPixmap(self.table_pixmap.scaled(self.mapLength,self.mapWidth))

        # Loading Picture Roboter 1 #
        self.picSizeRoboter = 40
        X_Coordinate_picRoboter = math.ceil((self.mapLength * 0.5) + self.mapXCoordinate - (self.picSizeRoboter/2))
        Y_Coordiante_picRoboter = math.ceil((self.mapWidth  * 0.5) + self.mapYCoordinate - (self.picSizeRoboter/2))
        self.picRoboter = QtGui.QLabel(MainWindow)
        self.picRoboter.setGeometry(X_Coordinate_picRoboter,Y_Coordiante_picRoboter,self.picSizeRoboter,self.picSizeRoboter)
        self.robot1_pixmap = QtGui.QPixmap(os.path.join(os.path.dirname(__file__), 'Robot1.png'))
        self.picRoboter.setPixmap(self.robot1_pixmap.scaled(self.picSizeRoboter,self.picSizeRoboter))

        # Lettering all GUI-Element #
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    """
    /*----------------------------------------------------------------------------------------------------
    Method: retranslateUi(self, MainWindow)
    ------------------------------------------------------------------------------------------------------
    This Method Lettering all GUI-Element
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow
    Output Parameter:       -
    ----------------------------------------------------------------------------------------------------*/
    """
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Eurobot 2015 Hauptsteuerung", None))
        self.lblGameStrategy.setText(_translate("MainWindow", "Strategie:", None))
        self.lblNumberofEnemy.setText(_translate("MainWindow", "Anzahl Gegner:", None))
        self.lblTeamColor.setToolTip(_translate("MainWindow", "Teamfarbe auswählen", None))
        self.lblTeamColor.setText(_translate("MainWindow", "Teamfarbe:", None))
        self.rbStrategyA.setText(_translate("MainWindow", "A", None))
        self.rbStrategyB.setText(_translate("MainWindow", "B", None))
        self.rbStrategyC.setText(_translate("MainWindow", "C", None))
        self.rbNumberofEnemy1.setText(_translate("MainWindow", "1", None))
        self.rbNumberofEnemy2.setText(_translate("MainWindow", "2", None))
        self.rbTeamColorYellow.setText(_translate("MainWindow", "Gelb", None))
        self.rbTeamColorGreen.setText(_translate("MainWindow", "Grün", None))
        self.lblTime.setText(_translate("MainWindow", "Verbleibende Spielzeit:", None))
        self.lblSettings.setText(_translate("MainWindow", "Einstellungen:", None))
        self.lblStatusInformation.setText(_translate("MainWindow", "Statusinformationen:", None))
        self.lblXPosition.setToolTip(_translate("MainWindow", "Teamfarbe auswählen", None))
        self.lblXPosition.setText(_translate("MainWindow", "X-Position: 0", None))
        self.lblYPosition.setText(_translate("MainWindow", "Y-Position: 0", None))
        self.lblAngle.setText(_translate("MainWindow", "Winkel: 0", None))
    """
    /*----------------------------------------------------------------------------------------------------
    Method: getAllSettingsString:
    ------------------------------------------------------------------------------------------------------
    This Method get all Settings back as a String
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow
    Output Parameter:       TeamColor     => Yellow/Green
                            NumberofEnemy => 1/2
                            Strategy      => A/B/C
    --------------------------------------------------------------------------------------------------*/
    """
    def getAllSettingsString(self):

        # Check Team Color #
        if self.rbTeamColorYellow.isChecked():
            TeamColor = "Yellow"
        elif self.rbTeamColorGreen.isChecked():
            TeamColor = "Green"

        # Check Stategy #
        if self.rbStrategyA.isChecked():
            Strategy = "A"
        elif self.rbStrategyB.isChecked():
            Strategy = "B"
        elif self.rbStrategyC.isChecked():
            Strategy = "C"

      # Check Number of Enemy #
        if self.rbNumberofEnemy1.isChecked():
            NumberofEnemy = "1"
        elif self.rbNumberofEnemy2.isChecked():
            NumberofEnemy = "2"

        # Return all Settings #
        return(TeamColor , NumberofEnemy, Strategy )
    """
    /*----------------------------------------------------------------------------------------------------
    Method: getAllSettings:
    ------------------------------------------------------------------------------------------------------
    This Method get all Settings back as a int
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow
    Output Parameter:       TeamColor     => 0/1
                            NumberofEnemy => 0/1
                            Strategy      => 0/1/2
    --------------------------------------------------------------------------------------------------*/
    """
    def getAllSettings(self):

        # Check Team Color #
        if self.rbTeamColorYellow.isChecked():
            TeamColor = 0
        elif self.rbTeamColorGreen.isChecked():
            TeamColor = 1

        # Check Stategy #
        if self.rbStrategyA.isChecked():
            Strategy = 0
        elif self.rbStrategyB.isChecked():
            Strategy = 1
        elif self.rbStrategyC.isChecked():
            Strategy = 2

      # Check Number of Enemy #
        if self.rbNumberofEnemy1.isChecked():
            NumberofEnemy = 0
        elif self.rbNumberofEnemy2.isChecked():
            NumberofEnemy = 1

        # Return all Settings #
        return(TeamColor , NumberofEnemy, Strategy )

    """
    /*----------------------------------------------------------------------------------------------------
    Method: setTeamColorRadioButton(self, TeamColor):
    ------------------------------------------------------------------------------------------------------
    This Method set the Radio Button from the Team Color
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow, TeamColor     => Yellow/Green
    Output Parameter:       -
    --------------------------------------------------------------------------------------------------*/
    """
    def setTeamColorRadioButton(self, TeamColor):
        if TeamColor == "Yellow":
            self.rbTeamColorYellow.setChecked(True)
            self.rbTeamColorYellow.setFocus()
        elif TeamColor == "Green":
            self.rbTeamColorGreen.setChecked(True)
            self.rbTeamColorGreen.setFocus()
    """
    /*----------------------------------------------------------------------------------------------------
    Method: setNumberofEnemyRadioButton(self, NumberofEnemy):
    ------------------------------------------------------------------------------------------------------
    This Method set the Radio Button from the Number of Enemy
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow, NumberofEnemy    => 1/2
    Output Parameter:       -
    --------------------------------------------------------------------------------------------------*/
    """
    def setNumberofEnemyRadioButton(self, NumberofEnemy):
        if NumberofEnemy == "1":
            self.rbNumberofEnemy1.setChecked(True)
            self.rbNumberofEnemy1.setFocus()
        elif NumberofEnemy == "2":
            self.rbNumberofEnemy2.setChecked(True)
            self.rbNumberofEnemy2.setFocus()

    """
    /*----------------------------------------------------------------------------------------------------
    Method: setStrategyRadioButton(self, Stategy):
    ------------------------------------------------------------------------------------------------------
    This Method set the Radio Button from the Stategy
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow, Stategy    => A/B/C
    Output Parameter:       -
    --------------------------------------------------------------------------------------------------*/
    """
    def setStrategyRadioButton(self, Stategy):
        if Stategy == "A":
            self.rbStrategyA.setChecked(True)
            self.rbStrategyA.setFocus()
        elif Stategy == "B":
            self.rbStrategyB.setChecked(True)
            self.rbStrategyB.setFocus()
        elif Stategy == "C":
            self.rbStrategyC.setChecked(True)
            self.rbStrategyC.setFocus()
    """
    /*----------------------------------------------------------------------------------------------------
    Method: setLCDTime(self, Stategy):
    ------------------------------------------------------------------------------------------------------
    This Method set LCD for the Game Time
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow, Time    => xx:xx
    Output Parameter:       -
    --------------------------------------------------------------------------------------------------*/
    """
    def setLCDTime(self, Time):
        self.lcdTime.display(Time)
    """
    /*----------------------------------------------------------------------------------------------------
    Method: setCoordinate(self, X_Coordinate, Y_Coordiante, Angle):
    ------------------------------------------------------------------------------------------------------
    This Method set the Status Information and the Draft of the actually Coordinates
    -----------------------------------------------------------------------------------------------------
    Input  Parameter:       MainWindow, (int) X_Coordinate (int) Coordiante, (int) Angle
    Output Parameter:       -
    --------------------------------------------------------------------------------------------------*/
    """
    def setCoordinate (self, X_Coordinate, Y_Coordinate, Angle):

        # Calculate in mm #
        X_Coordinate = math.ceil(X_Coordinate/10)
        Y_Coordinate = math.ceil(Y_Coordinate/10)

        # Print on Status Information #
        self.lblXPosition.setText(_translate("MainWindow", "X-Position: " + str(X_Coordinate), None))
        self.lblYPosition.setText(_translate("MainWindow", "Y-Position: " + str(Y_Coordinate), None))
        self.lblAngle.setText(_translate("MainWindow", "Winkel: " + str(Angle), None))

        # Calculate Position on the Map and draw it #
        self.X_Coordinate_picRoboter = math.ceil(((self.mapLength * X_Coordinate)/3000) + self.mapXCoordinate - (self.picSizeRoboter/2))
        self.Y_Coordinate_picRoboter = math.ceil(((self.mapWidth  * Y_Coordinate)/2000) + self.mapYCoordinate - (self.picSizeRoboter/2))

        self.picRoboter.setGeometry(self.X_Coordinate_picRoboter , self.Y_Coordinate_picRoboter , self.picSizeRoboter, self.picSizeRoboter)
