#! encoding = utf-8

""" Common functions shared by ui """

from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor
from math import ceil, floor


def create_double_spin_box(v, minimum=None, maximum=None, step=1., stepType=0,
                           dec=1, prefix=None, suffix=None):
    """ Create a QDoubleSpinBox with preset values """

    box = QtWidgets.QDoubleSpinBox()
    box.setSingleStep(step)
    box.setStepType(stepType)
    box.setDecimals(dec)

    # the Pythonic convention "if minimum:" cannot be used here,
    # incase minimum / maximum actually has value zero.
    if isinstance(minimum, type(None)):
        box.setMinimum(float('-inf'))
    else:
        box.setMinimum(minimum)

    if isinstance(maximum, type(None)):
        box.setMaximum(float('inf'))
    else:
        box.setMaximum(maximum)

    if prefix:
        box.setPrefix(prefix)
    else:
        pass

    if suffix:
        box.setSuffix(suffix)
    else:
        pass

    # one needs to set the value at last so that the value
    # does not get clipped by default minimum and maximum
    box.setValue(v)

    return box


def create_int_spin_box(v, minimum=None, maximum=None, step=1, stepType=0,
                        prefix=None, suffix=None):
    """ Create a QSpinBox with preset values """

    box = QtWidgets.QSpinBox()
    box.setStepType(stepType)
    box.setSingleStep(step)

    # the Pythonic convention "if minimum:" cannot be used here,
    # incase minimum / maximum actually has value zero.
    if isinstance(minimum, type(None)):
        box.setMinimum(-2147483648)
    else:
        box.setMinimum(floor(minimum))

    if isinstance(maximum, type(None)):
        box.setMaximum(2147483647)
    else:
        box.setMaximum(ceil(maximum))

    if prefix:
        box.setPrefix(prefix)
    else:
        pass

    if suffix:
        box.setSuffix(suffix)
    else:
        pass

    # one needs to set the value at last so that the value
    # does not get clipped by default minimum and maximum
    box.setValue(v)

    return box


def question(parent, title='', context=''):
    """ Return a question box
    :argument
        parent: QWiget          parent QWiget
        title: str              title string
        context: str            context string

    :returns
        ans: bool               If user clicked "yes"
    """

    q = QtWidgets.QMessageBox.question(parent, title, context,
                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                       QtWidgets.QMessageBox.Yes)
    ans = q == QtWidgets.QMessageBox.Yes
    return ans


def msg(title='', context='', style=''):
    """ Pop up a message box for information / warning
    :argument
        parent: QWiget          parent QWiget
        title: str              title string
        context: str            context string
        style: str              style of message box
            'info'              information box
            'warning'           warning box
            'critical'          critical box
    """

    if style == 'info':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, title, context)
    elif style == 'warning':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, title, context)
    elif style == 'critical':
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, title, context)
    else:
        d = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, title, context)
    d.exec_()


class ColorPicker(QtWidgets.QLabel):
    """ Pick color """

    def __init__(self, dialogColor, color='#000000', parent=None):
        super().__init__(parent)

        self.setFixedWidth(30)
        self.setFixedHeight(20)
        self.setStyleSheet('background-color: {:s}; border: 1pt'.format(color))
        self._color = color
        self._dialog = dialogColor

    def mouseReleaseEvent(self, ev):

        qc = QColor()
        qc.setNamedColor(self._color)
        self._dialog.setCurrentColor(qc)
        self._dialog.exec_()
        if self._dialog.result() == QtWidgets.QDialog.Accepted:
            self.color = self._dialog.selectedColor().name()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        try:
            self._color = color
            self.setStyleSheet('background-color: {:s}'.format(color))
            qc = QColor()
            qc.setNamedColor(color)
            self._dialog.setCurrentColor(qc)
        except Exception as err:
            msg(title='Color Picker Error', style='critical', context=str(err))

