# coding:utf-8
from PySide.QtUiTools import QUiLoader
from PySide import QtGui, QtCore
import os
import args
from function import Function


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]


class FunctionWidget(QtGui.QFrame):
    def __init__(self, fun):
        QtGui.QFrame.__init__(self)
        self.function = Function(fun)
        self.setLayout(QtGui.QFormLayout())
        self.layout().setLabelAlignment(QtCore.Qt.AlignRight)
        self.menu = QtGui.QMenu(self)
        self.menu.addAction("reset").triggered.connect(self.reset)
        self.menu.addAction("help").triggered.connect(self.help)
        self.argWidgets = AttributeDict()
        for key in self.function.args:
            if key in self.function.default:
                value = self.function.default[key]
                for ArgWidget in args.__all__:
                    label = " ".join([word.capitalize() for word in key.split("_")]) + " : "
                    arg_widget = ArgWidget.instance(value)
                    if arg_widget is not None:
                        self.layout().addRow(label, arg_widget)
                        self.argWidgets[key] = arg_widget
                        break
        self.kwargs = self.function.default

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.fn.fullName}')".format(self=self)

    @property
    def kwargs(self):
        return {key: value.arg for key, value in self.argWidgets.items()}

    @kwargs.setter
    def kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key in self.argWidgets:
                self.argWidgets[key].arg = value

    def reset(self):
        self.kwargs = self.function.default

    def help(self):
        QtGui.QMessageBox.about(self, "hlep", self.function.help)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())


class Window(object):
    loader = QUiLoader()
    ui_file = os.path.dirname(__file__)+"/window.ui"
    icons_dir = os.path.dirname(__file__)+"/icons/"

    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.name = kwargs.setdefault("name", "window")
        self.icon = kwargs.setdefault("name", "")
        self.typ = kwargs.setdefault("typ", "widget")
        self.window = None

    def show(self):
        if self.window:
            self.window.showNormal()
        else:
            self.window = self.loader.load(self.ui_file)
            self.window.setObjectName(self.name)
            self.window.setWindowIcon(QtGui.QIcon(self.icons_dir+self.icon))
            self.window.apply.clicked.connect(self.apply)
            self.window.setParent(QtGui.QApplication.activeWindow())
            self.window.setWindowFlags(QtCore.Qt.WindowFlags(1))
            self.window.showNormal()
            if self.typ == "widgets":
                self.window.functionTab = QtGui.QTabWidget()
                self.window.vlayout.insertWidget(0, self.window.functionTab)
                self.window.functionWidgets = AttributeDict()
                for fun in self.functions:
                    function_widget = FunctionWidget(fun)
                    label = " ".join([word.capitalize() for word in function_widget.function.name.split("_")])
                    self.window.functionWidgets[function_widget.function.name] = function_widget
                    self.window.functionTab.addTab(function_widget, label)
            elif self.typ == "widget":
                self.window.functionWidget = FunctionWidget(self.functions[0])
                self.window.vlayout.insertWidget(0, self.window.functionWidget)
                self.window.functionWidget.setFrameStyle(
                    self.window.functionWidget.Box | self.window.functionWidget.Raised)

    def apply(self):
        if self.typ == "widgets":
            function_widget = self.window.functionTab.currentWidget()
            function_widget.function(**function_widget.kwargs)
        elif self.typ == "widget":
            self.window.functionWidget.function(**self.window.functionWidget.kwargs)
        else:
            self.functions[0]()
