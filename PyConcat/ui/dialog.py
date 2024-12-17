#! encoding = utf-8

""" Dialog Windows """


from PyQt5 import QtWidgets, QtCore
from PyConcat.ui.common import create_int_spin_box, create_double_spin_box
from PyConcat.ui.common import ColorPicker
from PyConcat.libs.lib import VERSION


class DialogPref(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Dialog)

        self.setWindowTitle('Global Preference')
        # share a color dialog between color pickers (to save memory)
        self._colorDialog = QtWidgets.QColorDialog()
        penBox = QtWidgets.QGroupBox()
        penBox.setTitle('Pen')

        # pens for canavs, has color only
        self._canvas_pen_list = [
            ('bg', QtWidgets.QLabel('Background color'),
             ColorPicker(self._colorDialog, parent=self)),
        ]
        # pens for line, has color & width
        self._line_pen_list = [
            ('curve1', QtWidgets.QLabel('Curve 1'),
             ColorPicker(self._colorDialog, parent=self),
             create_int_spin_box(1, minimum=0, maximum=20, suffix=' px')),
            ('curve2', QtWidgets.QLabel('Curve 2'),
             ColorPicker(self._colorDialog, parent=self),
             create_int_spin_box(1, minimum=0, maximum=20, suffix=' px')),
        ]
        # pens for point, has color, width, and size
        self._pt_pen_list = []

        # other value input widgets
        self._inp_list = [
            ('click_radius', QtWidgets.QLabel('Click radius'),
             create_int_spin_box(3, minimum=1, maximum=10, suffix=' px')),
        ]

        # other check widgets
        self._ck_list = [
            ('is_antialias', QtWidgets.QCheckBox('Anti-alias')),
        ]

        penBoxLayout = QtWidgets.QGridLayout()
        row = 0
        penBoxLayout.addWidget(QtWidgets.QLabel('Color'), 0, 1)
        penBoxLayout.addWidget(QtWidgets.QLabel('Width'), 0, 2)
        penBoxLayout.addWidget(QtWidgets.QLabel('Size'), 0, 3)
        penBoxLayout.addWidget(QtWidgets.QLabel('Fill'), 0, 4)
        for _, qlabel, qcolor in self._canvas_pen_list:
            row += 1
            penBoxLayout.addWidget(qlabel, row, 0)
            penBoxLayout.addWidget(qcolor, row, 1)
        for _, qlabel, qcolor, qwidth in self._line_pen_list:
            row += 1
            penBoxLayout.addWidget(qlabel, row, 0)
            penBoxLayout.addWidget(qcolor, row, 1)
            penBoxLayout.addWidget(qwidth, row, 2)
        for _, qlabel, qcolor, qwidth, qsize, qck in self._pt_pen_list:
            row += 1
            penBoxLayout.addWidget(qlabel, row, 0)
            penBoxLayout.addWidget(qcolor, row, 1)
            penBoxLayout.addWidget(qwidth, row, 2)
            penBoxLayout.addWidget(qsize, row, 3)
            penBoxLayout.addWidget(qck, row, 4)
        penBox.setLayout(penBoxLayout)

        self.btnBox = QtWidgets.QDialogButtonBox()
        self.btnBox.addButton(QtWidgets.QDialogButtonBox.Cancel)
        self.btnBox.addButton(QtWidgets.QDialogButtonBox.Ok)

        otherLayout = QtWidgets.QFormLayout()
        for _, qlabel, qinp in self._inp_list:
            otherLayout.addRow(qlabel, qinp)
        for _, qck in self._ck_list:
            otherLayout.addRow(qck, None)

        thisLayout = QtWidgets.QGridLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop)
        thisLayout.addWidget(penBox, 0, 0)
        thisLayout.addLayout(otherLayout, 0, 1)
        thisLayout.addWidget(self.btnBox, 1, 0, 1, 2)
        self.setLayout(thisLayout)

        self.btnBox.accepted.connect(self.accept)
        self.btnBox.rejected.connect(self.reject)

    def load_prefs(self, prefs):

        for attr, _, qcolor in self._canvas_pen_list:
            qcolor.color = getattr(prefs, ''.join([attr, '_color']))
        for attr, _, qcolor, qwidth in self._line_pen_list:
            qcolor.color = getattr(prefs, ''.join([attr, '_color']))
            qwidth.setValue(getattr(prefs, ''.join([attr, '_width'])))
        for attr, _, qcolor, qwidth, qsize, qck in self._pt_pen_list:
            qcolor.color = getattr(prefs, ''.join([attr, '_color']))
            qwidth.setValue(getattr(prefs, ''.join([attr, '_width'])))
            qsize.setValue(getattr(prefs, ''.join([attr, '_size'])))
            qck.setChecked(getattr(prefs, ''.join([attr, '_fill'])))
        for attr, _, qinp in self._inp_list:
            qinp.setValue(getattr(prefs, attr))
        for attr, qck in self._ck_list:
            qck.setChecked(getattr(prefs, attr))

    def fetch_prefs_(self, prefs):
        """ Get current selected colors and write to prefs """

        for attr, _, qcolor in self._canvas_pen_list:
            setattr(prefs, ''.join([attr, '_color']), qcolor.color)
        for attr, _, qcolor, qwidth in self._line_pen_list:
            setattr(prefs, ''.join([attr, '_color']), qcolor.color)
            setattr(prefs, ''.join([attr, '_width']), qwidth.value())
        for attr, _, qcolor, qwidth, qsize, qck in self._pt_pen_list:
            setattr(prefs, ''.join([attr, '_color']), qcolor.color)
            setattr(prefs, ''.join([attr, '_width']), qwidth.value())
            setattr(prefs, ''.join([attr, '_size']), qsize.value())
            setattr(prefs, ''.join([attr, '_fill']), qck.isChecked())
        for attr, _, qinp in self._inp_list:
            setattr(prefs, attr, qinp.value())
        for attr, qck in self._ck_list:
            setattr(prefs, attr, qck.isChecked())


class DialogAbout(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.Dialog)

        self.setWindowTitle('About')


        self.label = QtWidgets.QLabel()
        self.label.setText(f"""
        Python spectra Concatenation Tool.
        Version {VERSION:s}
        Developed by Luyao Zou (https://github.com/luyaozou/PyConcat)

        This GUI tool is used to concatenate two spectra files into one file.
        Features include defining the scaling factor and average number for each spectrum to allow proper weight.
        It can also be used to simply perform spectral averages (given that two spectral files have the same frequency range).
        
        """)

        self.btnOk = QtWidgets.QPushButton('OK')
        self.btnOk.setFixedWidth(100)
        self.btnOk.clicked.connect(self.accept)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.addWidget(self.label)
        thisLayout.addWidget(self.btnOk)
        self.setLayout(thisLayout)
