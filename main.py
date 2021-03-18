# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QImage 
from PyQt5.QtCore import pyqtSlot, Qt, QPointF
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindowSlots():
    def exit_button():
        exit()

    def findDot(points,pos_x, pos_y):
        for i in range(len(points)):
            if((pos_x > (points[i].pos().x() - 12)) and (pos_x < (points[i].pos().x() + 12))):
                if((pos_y > (points[i].pos().y() - 12)) and (pos_y < (points[i].pos().y() + 12))):
                    return i

    def openMessage():
        tutorial = QMessageBox()
        tutorial.setWindowTitle("Instruction")
        tutorial.setText("Добро пожаловать в наше приложение!\n\n В приложении вы можете переключаться между 3 режимами:\n 1. Режим перемещения точек - Left Ctrl\n 2. Режим добавления точек - Left Ctrl\n 3. Режим удаления точек - Left Shift\n\n Информация о текущем режиме отображена в строке состояния.\n Для начала рисования необходимо добавить минимум 3 точки, и передвинуть одну из них.")
        tutorial.setIcon(QMessageBox.Information)
        tutorial.setStandardButtons(QMessageBox.Ok)
        tutorial.exec()


class MovingObject(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.setBrush(Qt.blue)
        self.setAcceptHoverEvents(True)
        self.redact = False

    def hoverEnterEvent(self, event):
        if(self.redact):
            app.instance().setOverrideCursor(Qt.OpenHandCursor)

    def hoverLeaveEvent(self, event):
        app.instance().restoreOverrideCursor()

    def mousePressEvent(self, event):
        pass


    def mouseMoveEvent(self, event):        
        super().mousePressEvent(event)
        if(self.redact):
            orig_cursor_position = event.lastScenePos()
            updated_cursor_position = event.scenePos()

            orig_position = self.scenePos()

            updated_cursor_x = updated_cursor_position.x() - orig_cursor_position.x() + orig_position.x()
            updated_cursor_y = updated_cursor_position.y() - orig_cursor_position.y() + orig_position.y()
            self.setPos(QPointF(updated_cursor_x, updated_cursor_y))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)        

class Test(QGraphicsView):
    def __init__(self, label):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()
        self.points = []
        self.isDraw = False
        self.drawedPath = None
        self.label = label

    def initUI(self):     
        self.scene = QGraphicsScene()
        self.setScene(self.scene)       
        self.setSceneRect(110, 100, 450, 350) 
        self.pressing = False  
        self.mouse_posX = None
        self.mouse_posY = None
        self.redact = False
        self.delete = False
        self.obj = None
        self.update()
    
        
    def keyPressEvent(self, QKeyEvent):
        super().keyPressEvent(QKeyEvent)
        if(QKeyEvent.key() == 16777249):  # "Left Ctrl" Button - needs for Redactor Mode On/Off
            if(self.redact):
                self.redact = False
                if(len(self.points) > 0):
                    for i in range(len(self.points)):
                        self.points[i].redact = True
                
                self.label.setText("Режим: перемещение точек")
                self.delete = False
                self.update()
            else:
                self.redact = True
                if(len(self.points) > 0):
                    for i in range(len(self.points)):
                        self.points[i].redact = False
                
                self.label.setText("Режим: добавление точек")                
                self.delete = False
                self.update()
        
        if(QKeyEvent.key() == 16777248):
            self.redact = False
            self.delete = True
            self.label.setText("Режим: удаления точек")

    def mousePressEvent(self, QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        self.mouse_posX = QMouseEvent.pos().x() + 80
        self.mouse_posY = QMouseEvent.pos().y() + 70
        self.pressing = True
        
        self.update()
                
        if not self.mouse_posX or not self.pressing:
            return

        if(self.redact and not self.delete):            
            self.obj = MovingObject(self.mouse_posX, self.mouse_posY, 12)
            self.scene.addItem(self.obj)
            self.points.append(self.obj)

        if(self.delete):
            i = MainWindowSlots.findDot(self.points, self.mouse_posX, self.mouse_posY)
            if i != None:
                self.scene.removeItem(self.points[i])
                self.points.pop(i)
            if( self.drawedPath != None and len(self.points) < 3):
                self.scene.removeItem(self.drawedPath)
                self.update() 
        
    
    def mouseReleaseEvent(self, QMouseEvent):
        super().mouseReleaseEvent(QMouseEvent)   
        self.pressing = False
        self.update()



    def paintEvent(self, event):
        super().paintEvent(event)
        if((len(self.points) > 2) ): #and not (self.redact)
            points = []
            for i in range(len(self.points)):
                points.append(QPoint(self.points[i].pos().x(),self.points[i].pos().y()))

            painter = QPainter(self)        
            path = QPainterPath()
            painter.setPen(QtCore.Qt.blue)
            painter.setBrush(QBrush(Qt.red, Qt.NoBrush))
            path.moveTo(points[0])

            for p, current in enumerate(points[1:-1], 1):
                #print(p)
                #print(current)
                # previous segment - серая линия
                source = QtCore.QLineF(points[p - 1], current)
                #print(source.length())
                # next segment - серая линия
                target = QtCore.QLineF(current, points[p + 1])
                #print(target.length())
                targetAngle = target.angleTo(source)
                #print(targetAngle)
                if targetAngle > 180:
                    angle = (source.angle() + source.angleTo(target) / 2) % 360
                else:
                    angle = (target.angle() + target.angleTo(source) / 2) % 360

                #print(target.angle())
                #print(angle)
                prop = 1/3
                #print(prop)

                revTarget = QtCore.QLineF.fromPolar(source.length() * prop, angle + 180).translated(current)
                cp2 = revTarget.p2()
                #print(cp2)

                if p == 1:
                    path.quadTo(cp2, current)
                else:
                    path.cubicTo(cp1, cp2, current)

                revSource = QtCore.QLineF.fromPolar(target.length() * prop, angle).translated(current)
                cp1 = revSource.p2()
                #print(cp1)

            # the final curve, that joins to the last point
            path.quadTo(cp1, points[-1])
            
            if((self.isDraw) and (self.drawedPath != None)):
                self.scene.removeItem(self.drawedPath)
            self.drawedPath = self.scene.addPath(path,QtCore.Qt.blue,QBrush(Qt.red, Qt.NoBrush))
            self.isDraw = True
            self.update()
        self.update()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)


        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(400, 70, 200, 20))
        self.label.setFont(QtGui.QFont("Times", 9, QtGui.QFont.Bold))
        self.label.setObjectName("label")
        self.label.setText("Режим: перемещение точек")
        
        self.test = Test(self.label)

        self.horizontalLayoutWidget_1 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_1.setGeometry(QtCore.QRect(110, 100, 500, 400))
        self.horizontalLayoutWidget_1.setObjectName("horizontalLayoutWidget_1")


        self.horizontalLayout_1 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_1)
        self.horizontalLayout_1.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")
        self.horizontalLayout_1.addWidget(self.test)


        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(630, 450, 160, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")


        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")


        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_2.clicked.connect(MainWindowSlots.exit_button)


        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(630, 70, 160, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")


        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")


        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton.clicked.connect(MainWindowSlots.openMessage)


        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "Exit"))
        self.pushButton.setText(_translate("MainWindow", "Tutorial"))

    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())