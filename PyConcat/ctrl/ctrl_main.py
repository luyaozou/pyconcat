#! encoding = utf-8

""" PSE main controller """


import numpy as np
from PyQt5 import QtWidgets
from os.path import isfile
try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 'importlib_resources'.
    import importlib_resources as resources
from PyConcat.libs.lib import get_abs_path, split_filename_dir, load_xy_file
from PyConcat.config import config
from PyConcat.ui.ui import MainUI, MenuBar
from PyConcat.ui.dialog import DialogPref, DialogAbout
from PyConcat.ui.common import msg


class PyCCMainWin(QtWidgets.QMainWindow):
    """ PSE main window """

    def __init__(self, nscreens):
        super().__init__()

        # Set global window properties
        self.setWindowTitle('Python Spectra Concatenation Tool')
        self.setMinimumWidth(1200)
        self.setMinimumHeight(800)
        self.setStyleSheet('font-size: 10pt')
        # self.setWindowIcon(QtGui.QIcon(get_abs_path('PyConcat.resources', 'pycc_logo.png')))

        # load settings
        self.prefs = config.Prefs()
        f = get_abs_path('PyConcat.config', 'prefs.json')
        if isfile(f):
            config.from_json_(self.prefs, f)
        self.prefs.nscreens = nscreens
        self.setGeometry(*self.prefs.geometry)
        self.dbconn = None          # db connection
        self.dbcursor = None        # db cursor

        # load main UI
        self.ui = MainUI(self.prefs, parent=self)

        # create dialog windows
        self.dPref = DialogPref(parent=self)
        self.dPref.load_prefs(self.prefs)
        self.dAbout = DialogAbout(parent=self)

        # set menu bar
        self.menuBar = MenuBar(self.prefs, parent=self)
        self.setMenuBar(self.menuBar)
        self.menuBar.actionPref.triggered.connect(self.dPref.exec)
        self.menuBar.actionAbout.triggered.connect(self.dAbout.exec)
        self.menuBar.actionExit.triggered.connect(self.close)

        # set central widget
        self.setCentralWidget(self.ui)

        # connect top-level signals
        self.dPref.accepted.connect(self.update_prefs)
        self.ui.box1.btnOpen.clicked.connect(self.open_file_1)
        self.ui.box2.btnOpen.clicked.connect(self.open_file_2)
        self.ui.box1.btnClear.clicked.connect(self.clear_file_1)
        self.ui.box2.btnClear.clicked.connect(self.clear_file_2)
        self.ui.box1.inpYShift.valueChanged[float].connect(self.shift_y1)
        self.ui.box2.inpYShift.valueChanged[float].connect(self.shift_y2)
        self.ui.box3.btnConcat.clicked.connect(self.concat)
        self.ui.box3.btnSave.clicked.connect(self.save)
        self.ui.box3.btnOverride.clicked.connect(self.override)
        self.ui.box3.btnClear.clicked.connect(self.clear_concat)

        # create data
        self.x1 = np.zeros(0)
        self.y1 = np.zeros(0)
        self.x2 = np.zeros(0)
        self.y2 = np.zeros(0)
        self.xt = np.zeros(0)
        self.yt = np.zeros(0)

    def closeEvent(self, ev):

        # save setting to local file
        f = get_abs_path('PyConcat.config', 'prefs.json')
        self.ui.fetch_prefs_(self.prefs)
        geo = self.geometry()
        self.prefs.geometry = (geo.x(), geo.y(), geo.width(), geo.height())
        config.to_json(self.prefs, f)
        self.close()

    def update_prefs(self):
        self.dPref.fetch_prefs_(self.prefs)
        self.ui.load_prefs(self.prefs)

    def _open_file_dialog(self, title):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, title, self.prefs.spec_dir, 'Spectral File (*.*)')
        if filename:
            self.prefs.spec_dir, _ = split_filename_dir(filename)
        return filename

    def open_file_1(self):
        try:
            filename = self._open_file_dialog('Open Data 1')
            if filename:
                data = load_xy_file(filename)
                self.x1 = data[:, 0]
                self.y1 = data[:, 1]
                self.ui.canvasFull.plot1(self.x1, self.y1)
                self.ui.canvasDetail.plot1(self.x1, self.y1)
                self._adjust_range()
        except Exception as e:
            msg('Error', str(e))

    def open_file_2(self):
        try:
            filename = self._open_file_dialog('Open Data 2')
            if filename:
                data = load_xy_file(filename)
                self.x2 = data[:, 0]
                self.y2 = data[:, 1]
                self.ui.canvasFull.plot2(self.x2, self.y2)
                self.ui.canvasDetail.plot2(self.x2, self.y2)
                self._adjust_range()
        except Exception as e:
            msg('Error', str(e))

    def clear_file_1(self):
        self.x1 = np.zeros(0)
        self.y1 = np.zeros(0)
        self.ui.canvasFull.plot1(np.zeros(0), np.zeros(0))
        self.ui.canvasDetail.plot1(np.zeros(0), np.zeros(0))
        self._adjust_range()

    def clear_file_2(self):
        self.x2 = np.zeros(0)
        self.y2 = np.zeros(0)
        self.ui.canvasFull.plot2(np.zeros(0), np.zeros(0))
        self.ui.canvasDetail.plot2(np.zeros(0), np.zeros(0))
        self._adjust_range()

    def shift_y1(self, val):
        self.ui.canvasFull.plot1(self.x1, self.y1 + val)
        self.ui.canvasDetail.plot1(self.x1, self.y1 + val)

    def shift_y2(self, val):
        self.ui.canvasFull.plot2(self.x2, self.y2 + val)
        self.ui.canvasDetail.plot2(self.x2, self.y2 + val)

    def _adjust_range(self):
        """ Adjust x range of the two curves """
        # full range
        if np.any(self.x1) and np.any(self.x2):
            xmin = min(self.x1.min(), self.x2.min())
            xmax = max(self.x1.max(), self.x2.max())
            self.ui.canvasFull.set_xrange(xmin, xmax)
            # detail range
            self.ui.canvasDetail.set_xrange(*self._find_overlap_range(
                self.x1.min(), self.x1.max(), self.x2.min(), self.x2.max()
            ))
        elif np.any(self.x1):
            self.ui.canvasFull.set_xrange(self.x1.min(), self.x1.max())
            self.ui.canvasDetail.set_xrange(self.x1.min(), self.x1.max())
        elif np.any(self.x2):
            self.ui.canvasFull.set_xrange(self.x2.min(), self.x2.max())
            self.ui.canvasDetail.set_xrange(self.x2.min(), self.x2.max())

    @staticmethod
    def _find_overlap_range(x1min, x1max, x2min, x2max):
        """ Find the overlap range of two x ranges """
        _l = [x1min, x1max, x2min, x2max]
        _l.sort()
        return _l[1], _l[2]

    def save(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, 'Save Concatenated', self.prefs.export_dir, 'Spectral File (*.txt)')
        if filename:
            self.prefs.export_dir, _ = split_filename_dir(filename)
            fmtX = self.ui.box3.inpFmtX.text()
            fmtY = self.ui.box3.inpFmtY.text()
            try:
                np.savetxt(filename, np.column_stack((self.xt, self.yt)), fmt=[fmtX, fmtY])
            except Exception as e:
                msg('Error', str(e))

    def concat(self):
        # get settings
        avg1 = self.ui.box1.inpAvg.value()
        scale1 = self.ui.box1.inpScale.value()
        avg2 = self.ui.box2.inpAvg.value()
        scale2 = self.ui.box2.inpScale.value()
        yshift1 = self.ui.box1.inpYShift.value()
        yshift2 = self.ui.box2.inpYShift.value()
        try:
            # get overlap xrange
            xo_min, xo_max = self._find_overlap_range(self.x1.min(), self.x1.max(), self.x2.min(), self.x2.max())
            # check if the dimension of the two data are identical
            x1_to_cat = self.x1[(self.x1 > xo_min) & (self.x1 < xo_max)]
            x2_to_cat = self.x2[(self.x2 > xo_min) & (self.x2 < xo_max)]
            y1_to_cat = self.y1[(self.x1 > xo_min) & (self.x1 < xo_max)] + yshift1
            y2_to_cat = self.y2[(self.x2 > xo_min) & (self.x2 < xo_max)] + yshift2
            if x1_to_cat.shape != x2_to_cat.shape:
                msg('Error', 'The two data have different dimensions')
                return None
        except Exception as e:
            msg('Error', str(e))
            return None
        # concatenate
        # 1. find left part
        if self.x1.min() < xo_min:
            x_left = self.x1[self.x1 <= xo_min]
            y_left = self.y1[self.x1 <= xo_min]
        else:
            x_left = self.x2[self.x2 <= xo_min]
            y_left = self.y2[self.x2 <= xo_min]
        # 2. find right part
        if self.x1.max() > xo_max:
            x_right = self.x1[self.x1 >= xo_max]
            y_right = self.y1[self.x1 >= xo_max]
        else:
            x_right = self.x2[self.x2 >= xo_max]
            y_right = self.y2[self.x2 >= xo_max]
        # 3. concatenate middle part
        y_cat = (y1_to_cat * avg1 * scale1 + y2_to_cat * avg2 * scale2) / (avg1 + avg2)
        # put everything together
        self.xt = np.concatenate((x_left, x1_to_cat, x_right))
        self.yt = np.concatenate((y_left, y_cat, y_right))
        # plot
        self.ui.canvasCC.plot1(self.xt, self.yt)
        if np.any(x1_to_cat):
            self.ui.canvasCC.plot2(x1_to_cat, y_cat)
        else:
            self.ui.canvasCC.curve2.clear()
        self.ui.canvasCC.set_xrange(self.xt.min(), self.xt.max())

    def override(self):
        self.x1 = self.xt
        self.y1 = self.yt
        self.ui.canvasFull.curve1.setData(self.x1, self.y1)
        self.ui.canvasDetail.curve1.setData(self.x1, self.y1)
        self._adjust_range()

    def clear_concat(self):
        self.xt = np.zeros(0)
        self.yt = np.zeros(0)
        self.ui.canvasCC.plot1(np.zeros(0), np.zeros(0))
        self.ui.canvasCC.plot2(np.zeros(0), np.zeros(0))
        self._adjust_range()
