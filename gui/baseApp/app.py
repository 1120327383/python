#!/usr/bin/python
#coding=utf-8
import sys
import xlrd
from PyQt5 import QtCore, QtGui
from PyQt5 import QtWidgets
from ui_form import Ui_dialog
import threading
import time


class MyTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent):
        self.parent=parent
        super(MyTableWidget, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(MyTableWidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(MyTableWidget, self).dragMoveEvent(event)
        event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            #遍历输出拖动进来的所有文件路径
            for url in event.mimeData().urls():
                print (url.toLocalFile())
                self.parent.filename= url.toLocalFile()
                self.set_data()
            event.acceptProposedAction()
        else:
            super(MyTableWidget,self).dropEvent(event)

    def set_data(self):
            rb=xlrd.open_workbook(self.parent.filename)
            sh=rb.sheet_by_index(0)
            rows=sh.row_values(0)
            self.parent.toast(rows)


class MyThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str) # trigger传输的内容是字符串
    def __init__(self, parent=None):
        self.parent=parent
        super(MyThread, self).__init__(parent)

    def start_job(self):
        while True:
            time.sleep(2)
            self.trigger.emit(u'启动,开始登录')
    def run(self):
        t=threading.Thread(target=self.start_job,args=())
        t.setDaemon(True)
        t.start()

class UItest(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.Gui()
        self.setlisteners()

    def load_data(self):
        rb=xlrd.open_workbook("D:/list.xls")
        sh1=rb.sheet_by_index(0)
        self.words=sh1.col_values(0)
        sh2=rb.sheet_by_index(1)
        self.phones=sh2.col_values(0)
        self.pwds=sh2.col_values(1)

    def init_table_widget(self):
        self.tableWidget = MyTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(5, 10, 618, 341))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(20)
        self.tableWidget.setHorizontalHeaderLabels([u'登录手机号',u'登录密码',u'姓名',u'地址',u'手机号',u'预约结果'])
        self.tableWidget.setColumnWidth(0, 120)
        self.tableWidget.setColumnWidth(1, 120)
        self.tableWidget.setColumnWidth(2, 70)
        self.tableWidget.setAlternatingRowColors(True)

    def setlisteners(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/res/finderf.bmp"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.ui.pushButton_5.clicked.connect(self.launch)
        self.ui.label_3.setAutoFillBackground(True)
        self.ui.label_3.setBackgroundRole(1)


    def toast(self, message):
        #self.ui.text_area.insertPlainText(message+"\n") # use insertPlainText to prevent the extra newline character
        cursor = self.ui.text_area.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        if type(message)== str:
            cursor.insertText(message + "\n")
        else:
            cursor.insertText(",".join(message)+"\n")
        self.ui.text_area.setTextCursor(cursor)
        self.ui.text_area.ensureCursorVisible()

    def launch(self):
        self.toast(u'start')
        self.job=MyThread(self)
        self.job.trigger.connect(self.toast)
        self.job.run()
    def Gui(self):
        self.ui = Ui_dialog()
        self.ui.setupUi(self)
        self.init_table_widget()
        self.show()

app = QtWidgets.QApplication(sys.argv)
myqq = UItest()
sys.exit(app.exec_())