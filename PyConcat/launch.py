#! encoding = utf-8

""" Launch PyConcat GUI """

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import platform
import ctypes
from PyConcat.ctrl.ctrl_main import PyCCMainWin


def launch():

    # fix the bug of bad scaling on screens of different DPI
    if platform.system() == 'Windows':
        if int(platform.release()) >= 8:
            ctypes.windll.shcore.SetProcessDpiAwareness(True)

    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei UI', 12))

    window = PyCCMainWin(len(app.screens()))
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':

    launch()
