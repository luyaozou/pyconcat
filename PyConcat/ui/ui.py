#! encoding = utf-8

""" Canvas widgets """


from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from numpy import median, any
from PyConcat.ui.common import create_int_spin_box, create_double_spin_box


class MainUI(QtWidgets.QWidget):

    def __init__(self, prefs, parent=None):
        super().__init__(parent)

        self.penMgr = PenManager(prefs)
        pg.setConfigOption('leftButtonPan', False)

        self.canvasFull = Canvas(self.penMgr, parent=self)
        self.canvasDetail = Canvas(self.penMgr, parent=self)
        self.canvasDetail.setYLink(self.canvasFull)
        self.canvasCC = Canvas(self.penMgr, parent=self)
        self.canvasCC.setXLink(self.canvasFull)
        self.canvasCC.setYLink(self.canvasFull)
        canvasLayout = QtWidgets.QVBoxLayout()  # _layout for canvas
        canvasLayout.addWidget(self.canvasFull)
        canvasLayout.addWidget(self.canvasDetail)
        canvasLayout.addWidget(self.canvasCC)

        # control buttons
        self.box1 = BoxFile('File 1')
        self.box2 = BoxFile('File 2')
        self.box3 = BoxConcat()

        btnLayout = QtWidgets.QVBoxLayout()
        btnLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        btnLayout.addWidget(self.box1)
        btnLayout.addWidget(self.box2)
        btnLayout.addWidget(self.box3)
        btns = QtWidgets.QWidget()
        btns.setFixedWidth(300)
        btns.setLayout(btnLayout)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(canvasLayout)
        mainLayout.addWidget(btns)

        self.setLayout(mainLayout)
        self.load_prefs(prefs)

    def load_prefs(self, prefs):
        self.box1.inpAvg.setValue(prefs.avg1)
        self.box1.inpScale.setValue(prefs.scale1)
        self.box2.inpAvg.setValue(prefs.avg2)
        self.box2.inpScale.setValue(prefs.scale2)
        self.box3.inpFmtX.setText(prefs.fmtX)
        self.box3.inpFmtY.setText(prefs.fmtY)
        self.penMgr.load_prefs(prefs)
        self.canvasFull.refreshPen()
        self.canvasDetail.refreshPen()
        self.canvasCC.refreshPen()

    def fetch_prefs_(self, prefs):
        prefs.avg1 = self.box1.inpAvg.value()
        prefs.scale1 = self.box1.inpScale.value()
        prefs.avg2 = self.box2.inpAvg.value()
        prefs.scale2 = self.box2.inpScale.value()
        prefs.fmtX = self.box3.inpFmtX.text()
        prefs.fmtY = self.box3.inpFmtY.text()


class Canvas(pg.PlotWidget):

    def __init__(self, penMgr, parent=None):
        super().__init__(parent)

        self._penMgr = penMgr
        self._ptItem_dict = {}      # saves all assigned peak items
        self.curve1 = pg.PlotCurveItem()
        self.curve2 = pg.PlotCurveItem()
        self.addItem(self.curve1)
        self.addItem(self.curve2)
        self.setLabel('bottom', 'Frequency')
        self.refreshPen()

        # keep track of the xrange of the spectrum
        self._xrange_record = []
        self._x1 = 0.    # hold the current mouse position 1
        self._x2 = 1.    # hold the current mouse position 2
        self._ymin = -100.   # hold the current y range
        self._ymax = 100.    # hold the current y range
        self._ymedian = 0.     # hold the current y center

    def plot1(self, x, y):
        self.curve1.setData(x, y)
        if any(y):
            self._ymin = max(y.min(), self._ymin)
            self._ymax = min(y.max(), self._ymax)
        if any(self.curve2.yData):
            self._ymedian = (median(y) + median(self.curve2.yData)) / 2
        else:
            self._ymedian = median(y)

    def plot2(self, x, y):
        self.curve2.setData(x, y)
        if any(y):
            self._ymin = max(y.min(), self._ymin)
            self._ymax = min(y.max(), self._ymax)
        if any(self.curve1.yData):
            self._ymedian = (median(y) + median(self.curve1.yData)) / 2
        else:
            self._ymedian = median(y)

    def refreshPen(self):

        self.setBackground(self._penMgr.get_color('bg'))
        self.curve1.setPen(self._penMgr.get_pen('curve1'))
        self.curve2.setPen(self._penMgr.get_pen('curve2'))
        self.curve1.opts['antialias'] = self._penMgr.is_antialias
        self.curve2.opts['antialias'] = self._penMgr.is_antialias

    def get_current_xrange(self):
        if self._xrange_record:
            return self._xrange_record[-1]
        else:
            return self.curve1.xData.min(), self.curve1.xData.max()

    def get_current_yrange(self):
        view_range = self.curve1.getViewBox().viewRange()
        return view_range[1]

    def set_xrange(self, xmin, xmax):
        self._x1 = xmin
        self._x2 = xmax
        self._xrange_record = [(self._x1, self._x2), ]
        self.curve1.getViewBox().setXRange(self._x1, self._x2)

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            self._x1 = self.getViewBox().mapSceneToView(ev.pos()).x()
        else:
            pass

    def mouseReleaseEvent(self, ev):
        viewBox = self.curve1.getViewBox()
        if ev.button() == QtCore.Qt.RightButton:
            # go to the previous xrange unless it cannot go further
            if len(self._xrange_record) > 1:
                self._xrange_record.pop()
            xmin, xmax = self._xrange_record[-1]
            viewBox.setXRange(xmin, xmax)
        elif ev.button() == QtCore.Qt.LeftButton:
            # find out the new xrange
            self._x2 = viewBox.mapSceneToView(ev.pos()).x()
            # determine if x2-x1 is larger than 10 times resolution
            # if yes, it means zoom in action
            # if not, it means a simple click
            diff = (self._x2 - self._x1)
            # get current viewbox range
            xrange, yrange = viewBox.viewRange()
            # get current viewbox length
            boxwidth = viewBox.screenGeometry().width()
            # calculate selection range by radius
            xradius = self._penMgr.click_radius / boxwidth * (xrange[1] - xrange[0])
            if abs(diff) > 3 * xradius:
                if self._x2 > self._x1:
                    self._xrange_record.append((self._x1, self._x2))
                    viewBox.setXRange(self._x1, self._x2)
                elif self._x2 < self._x1:
                    self._xrange_record.append((self._x2, self._x1))
                    viewBox.setXRange(self._x2, self._x1)
            else:   # simple click, emit mouse click signal
                pass
        else:
            pass

    def wheelEvent(self, ev):
        if ev.modifiers() == QtCore.Qt.ControlModifier:
            if ev.angleDelta().y() > 0:
                self._zoom_y(1.25)
            else:
                self._zoom_y(0.8)

    def _zoom_y(self, factor):
        self._ymin = (self._ymin - self._ymedian) / factor + self._ymedian
        self._ymax = (self._ymax - self._ymedian) / factor + self._ymedian
        self.curve1.getViewBox().setYRange(self._ymin, self._ymax)


class BoxFile(QtWidgets.QGroupBox):

    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setTitle(title)

        self.btnOpen = QtWidgets.QPushButton('Open File')
        self.inpAvg = create_int_spin_box(1, minimum=1)
        self.inpScale = create_double_spin_box(1, minimum=0, dec=3)
        self.inpScale.setStepType(QtWidgets.QAbstractSpinBox.AdaptiveDecimalStepType)
        self.btnClear = QtWidgets.QPushButton('Clear')

        avgLayout = QtWidgets.QHBoxLayout()
        avgLayout.addWidget(QtWidgets.QLabel('Average: '))
        avgLayout.addWidget(self.inpAvg)

        scaleLayout = QtWidgets.QHBoxLayout()
        scaleLayout.addWidget(QtWidgets.QLabel('Scale: '))
        scaleLayout.addWidget(self.inpScale)

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        thisLayout.addWidget(self.btnOpen)
        thisLayout.addLayout(avgLayout)
        thisLayout.addLayout(scaleLayout)
        thisLayout.addWidget(self.btnClear)
        self.setLayout(thisLayout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)


class BoxConcat(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Concatenated')

        self.btnConcat = QtWidgets.QPushButton('Concatenate')
        self.btnOverride = QtWidgets.QPushButton('Override File 1')
        self.btnSave = QtWidgets.QPushButton('Save (Ctrl+S)')
        self.btnSave.setShortcut('Ctrl+S')
        self.btnClear = QtWidgets.QPushButton('Clear')
        self.inpFmtX = QtWidgets.QLineEdit('%.2f')
        self.inpFmtX.setPlaceholderText('e.g. %.2f')
        self.inpFmtY = QtWidgets.QLineEdit('%.3f')
        self.inpFmtY.setPlaceholderText('e.g. %.2f')

        fmtXLayout = QtWidgets.QHBoxLayout()
        fmtXLayout.addWidget(QtWidgets.QLabel('X Format: '))
        fmtXLayout.addWidget(self.inpFmtX)
        fmtXLayout.addStretch()

        fmtYLayout = QtWidgets.QHBoxLayout()
        fmtYLayout.addWidget(QtWidgets.QLabel('Y Format: '))
        fmtYLayout.addWidget(self.inpFmtY)
        fmtYLayout.addStretch()

        thisLayout = QtWidgets.QVBoxLayout()
        thisLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        thisLayout.addWidget(self.btnConcat)
        thisLayout.addWidget(self.btnOverride)
        thisLayout.addWidget(self.btnSave)
        thisLayout.addWidget(self.btnClear)
        thisLayout.addLayout(fmtXLayout)
        thisLayout.addLayout(fmtYLayout)
        self.setLayout(thisLayout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)


class PenManager:
    """ A global pen manager for all canvas. This makes sure the same pen
    and brush are re-used in all pyqtgraph widgets to allow faster rendering
    """

    color_names = ('bg',)
    line_names = ('curve1', 'curve2',)
    pt_names = ()

    def __init__(self, prefs):
        self._dict_color = {}
        self._dict_pen = {}
        self._dict_size = {}
        self._dict_brush = {}
        self.is_antialias = True
        self.click_radius = 3
        self.load_prefs(prefs)

    def load_prefs(self, prefs):
        self.click_radius = prefs.click_radius
        self.is_antialias = prefs.is_antialias
        for name in self.color_names:
            self._dict_color[name] = pg.mkColor(
                    getattr(prefs, '_'.join([name, 'color']))
            )
        for name in self.line_names:
            self._dict_pen[name] = pg.mkPen(
                    color=getattr(prefs, '_'.join([name, 'color'])),
                    width=getattr(prefs, '_'.join([name, 'width']))
            )
        for name in self.pt_names:
            self._dict_pen[name] = pg.mkPen(
                    color=getattr(prefs, '_'.join([name, 'color'])),
                    width=getattr(prefs, '_'.join([name, 'width']))
            )
            self._dict_size[name] = getattr(prefs, '_'.join([name, 'size']))
            if getattr(prefs, '_'.join([name, 'fill'])):
                self._dict_brush[name] = pg.mkBrush(
                        color=getattr(prefs, '_'.join([name, 'color']))
                )
            else:
                self._dict_brush[name] = pg.mkBrush(None)

    def get_color(self, name):
        return self._dict_color[name]

    def get_pen(self, name):
        return self._dict_pen[name]

    def get_brush(self, name):
        return self._dict_brush[name]

    def get_size(self, name):
        return self._dict_size[name]


class MenuBar(QtWidgets.QMenuBar):

    def __init__(self, prefs, parent=None):
        super().__init__(parent)

        self.actionPref = QtWidgets.QAction('Preference')
        self.actionPref.setShortcut('Ctrl+P')
        self.actionAbout = QtWidgets.QAction('About')
        self.actionExit = QtWidgets.QAction('Exit')
        menuFile = self.addMenu('&Program')
        menuFile.addAction(self.actionPref)
        menuFile.addAction(self.actionAbout)
        menuFile.addAction(self.actionExit)
