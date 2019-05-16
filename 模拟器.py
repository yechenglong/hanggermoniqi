import sys

from PyQt5 import QtWidgets, QtGui
import 模拟器UI
import 产线
import 工站

class moniqi(QtWidgets.QWidget, 模拟器UI.Ui_Form):
    def __init__(self):
        super(moniqi, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.showchanxian)
        self.pushButton_2.clicked.connect(self.showgongzhan)

    def showgongzhan(self):
        for gongzhan in range(int(self.lineEdit_2.text())):
            gongzhan = 工站.gongzhan()
            gongzhan.show()

    def showchanxian(self):
        for chanxian in range(int(self.lineEdit.text())):
            chanxian = 产线.MotorLan()
            chanxian.show()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = moniqi()
    win.show()
    sys.exit(app.exec_())
