# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'label.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2560, 1440)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.image_label = QtWidgets.QLabel(self.centralwidget)
        self.image_label.setGeometry(QtCore.QRect(120, 20, 1024, 1024))
        # self.image_label.setGeometry(QtCore.QRect(0, 0, 1280, 720))
        self.image_label.setObjectName("image_label")

        ######################################################################
        # self.scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        # self.scroll_area.setGeometry(QtCore.QRect(384, 104, 520, 520))
        # self.scroll_area.setObjectName("scroll_area")
        # self.scroll_area.setWidget(self.image_label)
        # self.scroll_area.setWidgetResizable(True)

        # self.zoom_in = QtWidgets.QPushButton('Zoom in', self.centralwidget)
        # self.zoom_in.setGeometry(QtCore.QRect(384, 640, 120, 60))
        # self.zoom_out = QtWidgets.QPushButton('Zoom out', self.centralwidget)
        # self.zoom_out.setGeometry(QtCore.QRect(584, 640, 120, 60))
        # self.recover = QtWidgets.QPushButton('recover', self.centralwidget)
        # self.recover.setGeometry(QtCore.QRect(784, 640, 120, 60))

        ######################################################################

        self.image_label2 = QtWidgets.QLabel(self.centralwidget)
        self.image_label2.setGeometry(QtCore.QRect(1280, 0, 640, 360))
        self.image_label2.setObjectName("image_label2")

        self.image_label3 = QtWidgets.QLabel(self.centralwidget)
        self.image_label3.setGeometry(QtCore.QRect(1280, 360, 640, 360))
        self.image_label3.setObjectName("image_label3")

        self.slider_videoframe = QtWidgets.QSlider(self.centralwidget)
        self.slider_videoframe.setGeometry(QtCore.QRect(320, 1045, 640, 30))
        self.slider_videoframe.setOrientation(QtCore.Qt.Horizontal)
        self.slider_videoframe.setObjectName("slider_videoframe")

        self.label_framecnt = QtWidgets.QLabel(self.centralwidget)
        self.label_framecnt.setGeometry(QtCore.QRect(975, 1050, 100, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.label_framecnt.setFont(font)
        self.label_framecnt.setObjectName("label_framecnt")

        # self.button_play = QtWidgets.QPushButton(self.centralwidget)
        # self.button_play.setGeometry(QtCore.QRect(880, 725, 80, 40))
        # font = QtGui.QFont()
        # font.setPointSize(13)
        # self.button_play.setFont(font)
        # self.button_play.setObjectName("button_play")

        # self.button_pause = QtWidgets.QPushButton(self.centralwidget)
        # self.button_pause.setGeometry(QtCore.QRect(980, 725, 80, 40))
        # font = QtGui.QFont()
        # font.setPointSize(13)
        # self.button_pause.setFont(font)
        # self.button_pause.setMouseTracking(False)
        # self.button_pause.setObjectName("button_pause")

        self.message_box = QtWidgets.QLabel(self.centralwidget)
        self.message_box.setGeometry(QtCore.QRect(1300, 1020, 600, 30))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.message_box.setFont(font)
        self.message_box.setObjectName("message_box")

        # left-bottom block
        self.left_bot_block = QtWidgets.QFrame(self.centralwidget)
        self.left_bot_block.setGeometry(QtCore.QRect(0, 1080, 880, 290))
        self.left_bot_block.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.left_bot_block.setFrameShadow(QtWidgets.QFrame.Raised)
        self.left_bot_block.setObjectName("left_bot_block")

        self.label = QtWidgets.QLabel(self.left_bot_block)
        self.label.setGeometry(QtCore.QRect(30, 10, 180, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.left_bot_block)
        self.label_2.setGeometry(QtCore.QRect(30, 80, 180, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.left_bot_block)
        self.label_3.setGeometry(QtCore.QRect(30, 150, 180, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")

        self.label_filepath = QtWidgets.QLabel(self.left_bot_block)
        self.label_filepath.setGeometry(QtCore.QRect(30, 210, 1280, 70))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_filepath.setFont(font)
        self.label_filepath.setObjectName("label_filepath")

        self.combobox_data_type = QtWidgets.QComboBox(self.left_bot_block)
        self.combobox_data_type.setGeometry(QtCore.QRect(220, 20, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.combobox_data_type.setFont(font)
        self.combobox_data_type.setObjectName("combobox_data_type")

        self.combobox_basic = QtWidgets.QComboBox(self.left_bot_block)
        self.combobox_basic.setGeometry(QtCore.QRect(220, 90, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.combobox_basic.setFont(font)
        self.combobox_basic.setObjectName("combobox_basic")

        self.combobox_variant = QtWidgets.QComboBox(self.left_bot_block)
        self.combobox_variant.setGeometry(QtCore.QRect(220, 160, 300, 40))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.combobox_variant.setFont(font)
        self.combobox_variant.setObjectName("combobox_variant")

        self.label_basic = QtWidgets.QLabel(self.left_bot_block)
        self.label_basic.setGeometry(QtCore.QRect(540, 90, 100, 40))
        self.label_basic.setObjectName("label_basic")

        self.label_varient = QtWidgets.QLabel(self.left_bot_block)
        self.label_varient.setGeometry(QtCore.QRect(540, 160, 100, 40))
        self.label_varient.setObjectName("label_varient")

        self.backButton_basic = QtWidgets.QPushButton(self.left_bot_block)
        self.backButton_basic.setGeometry(QtCore.QRect(620, 90, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.backButton_basic.setFont(font)
        self.backButton_basic.setObjectName("backButton_basic")

        self.backButton_variant = QtWidgets.QPushButton(self.left_bot_block)
        self.backButton_variant.setGeometry(QtCore.QRect(620, 160, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.backButton_variant.setFont(font)
        self.backButton_variant.setObjectName("backButton_variant")

        self.nextButton_basic = QtWidgets.QPushButton(self.left_bot_block)
        self.nextButton_basic.setGeometry(QtCore.QRect(740, 90, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.nextButton_basic.setFont(font)
        self.nextButton_basic.setObjectName("nextButton_basic")

        self.nextButton_variant = QtWidgets.QPushButton(self.left_bot_block)
        self.nextButton_variant.setGeometry(QtCore.QRect(740, 160, 100, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.nextButton_variant.setFont(font)
        self.nextButton_variant.setObjectName("nextButton_variant")

        # center-bottom block
        self.center_bot_block = QtWidgets.QFrame(self.centralwidget)
        self.center_bot_block.setGeometry(QtCore.QRect(890, 1080, 780, 290))
        self.center_bot_block.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.center_bot_block.setFrameShadow(QtWidgets.QFrame.Raised)
        self.center_bot_block.setObjectName("center_bot_block")

        self.label_4 = QtWidgets.QLabel(self.center_bot_block)
        self.label_4.setGeometry(QtCore.QRect(30, 20, 180, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")

        self.combobox_frameNum = QtWidgets.QComboBox(self.center_bot_block)
        self.combobox_frameNum.setGeometry(QtCore.QRect(240, 30, 400, 40))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.combobox_frameNum.setFont(font)
        self.combobox_frameNum.setObjectName("combobox_frameNum")

        self.label_frame = QtWidgets.QLabel(self.center_bot_block)
        self.label_frame.setGeometry(QtCore.QRect(670, 25, 100, 60))
        self.label_frame.setObjectName("label_frame")

        self.color = QtWidgets.QLabel(self.center_bot_block)
        self.color.setGeometry(QtCore.QRect(30, 100, 190, 60))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.color.setFont(font)
        self.color.setObjectName("color")

        self.colorR = QtWidgets.QSpinBox(self.center_bot_block)
        self.colorR.setGeometry(QtCore.QRect(240, 110, 80, 50))
        self.colorR.setRange(0, 255)
        self.colorR.setValue(255)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.colorR.setFont(font)
        self.colorR.setObjectName("colorR")

        self.colorG = QtWidgets.QSpinBox(self.center_bot_block)
        self.colorG.setGeometry(QtCore.QRect(340, 110, 80, 50))
        self.colorG.setRange(0, 255)
        self.colorG.setValue(0)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.colorG.setFont(font)
        self.colorG.setObjectName("colorG")

        self.colorB = QtWidgets.QSpinBox(self.center_bot_block)
        self.colorB.setGeometry(QtCore.QRect(440, 110, 80, 50))
        self.colorB.setRange(0, 255)
        self.colorB.setValue(0)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.colorB.setFont(font)
        self.colorB.setObjectName("colorB")

        self.color_vis = QtWidgets.QLabel(self.center_bot_block)
        self.color_vis.setGeometry(QtCore.QRect(590, 80, 50, 110))
        self.color_vis.setObjectName("color_vis")

        self.auto_label = QtWidgets.QPushButton(self.center_bot_block)
        self.auto_label.setGeometry(QtCore.QRect(30, 200, 160, 60))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.auto_label.setFont(font)
        self.auto_label.setObjectName("auto_label")

        self.backButton_frame = QtWidgets.QPushButton(self.center_bot_block)
        self.backButton_frame.setGeometry(QtCore.QRect(240, 200, 160, 60))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.backButton_frame.setFont(font)
        self.backButton_frame.setObjectName("backButton_frame")

        self.nextButton_frame = QtWidgets.QPushButton(self.center_bot_block)
        self.nextButton_frame.setGeometry(QtCore.QRect(480, 200, 160, 60))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.nextButton_frame.setFont(font)
        self.nextButton_frame.setObjectName("nextButton_frame")

        # right-bottom block
        self.right_bot_block = QtWidgets.QFrame(self.centralwidget)
        self.right_bot_block.setGeometry(QtCore.QRect(1680, 1080, 240, 290))
        self.right_bot_block.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.right_bot_block.setFrameShadow(QtWidgets.QFrame.Raised)
        self.right_bot_block.setObjectName("right_bot_block")

        self.pushButton_add = QtWidgets.QPushButton(self.right_bot_block)
        self.pushButton_add.setGeometry(QtCore.QRect(35, 20, 170, 70))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton_add.setFont(font)
        self.pushButton_add.setObjectName("pushButton_add")

        self.pushButton_clear = QtWidgets.QPushButton(self.right_bot_block)
        self.pushButton_clear.setGeometry(QtCore.QRect(35, 110, 170, 70))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton_clear.setFont(font)
        self.pushButton_clear.setObjectName("pushButton_clear")

        self.pushButton_save = QtWidgets.QPushButton(self.right_bot_block)
        self.pushButton_save.setGeometry(QtCore.QRect(35, 200, 170, 70))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.pushButton_save.setFont(font)
        self.pushButton_save.setObjectName("pushButton_save")

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        # self.lbc_view.setText(_translate("MainWindow", "video_player"))

        self.label_framecnt.setText(_translate("MainWindow", "000/000"))
        # self.button_play.setText(_translate("MainWindow", "Play"))
        # self.button_pause.setText(_translate("MainWindow", "Pause"))
        self.message_box.setText(_translate(
            "MainWindow", "Note: Please select the pixel on top view image"))

        self.label.setText(_translate("MainWindow", "Data type: "))
        self.label_2.setText(_translate("MainWindow", "Basic scenario: "))
        self.label_3.setText(_translate("MainWindow", "Variant  scenario: "))
        self.label_4.setText(_translate("MainWindow", "Frame No. : "))
        self.color.setText(_translate("MainWindow", "Instance Color:"))
        self.label_filepath.setText(_translate("MainWindow", "Path:"))

        self.image_label.setText(_translate("MainWindow", "TextLabel"))

        self.nextButton_basic.setText(_translate("MainWindow", "Next"))
        self.backButton_basic.setText(_translate("MainWindow", "Back"))
        self.label_basic.setText(_translate("MainWindow", "000:000"))

        self.nextButton_variant.setText(_translate("MainWindow", "Next"))
        self.backButton_variant.setText(_translate("MainWindow", "Back"))
        self.label_varient.setText(_translate("MainWindow", "000:000"))

        self.auto_label.setText(_translate("MainWindow", "Auto Save"))
        self.nextButton_frame.setText(_translate("MainWindow", "Next"))
        self.backButton_frame.setText(_translate("MainWindow", "Back"))
        # self.label_frame.setText(_translate("MainWindow", ":"))

        self.pushButton_add.setText(_translate("MainWindow", "Add Zone"))
        self.pushButton_clear.setText(_translate("MainWindow", "Clean Points"))
        self.pushButton_save.setText(_translate("MainWindow", "Save Image"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
