# coding:utf-8

u"""
参数组件模块;
所有组建均继承自QtGui.QWidget;
每种组件对应一种参数类型;
组件的arg属性,用来查询/更改组件代表的数值;
组件的argChang信号，组件数值改变时发射;

Bool:勾选框<bool>
BoolArray:勾选框组<list[bool,bool……]>
Int:整数输入框<int>
IntArray:整数输入框组<list[int,int……]>
Float:浮点数输入框<int>
FloatArray:浮点数输入框组<list[float,float……]>
String: 文本输入框<str>
Enum:下拉菜单<str>
Path: 文件选择框<str>
PathArray: 文件列表框<list[str, str……]>
"""

from PySide import QtGui, QtCore
import re
import os
import sys


class AttributeDict(dict):
    def __getattr__(self, attr):
        return self[attr]


class enum(object):

    def __init__(self, *items):
        self.data = AttributeDict()
        self.data.index = 0
        self.data.item = items[0]
        self.data.items_tuple = items

    def __int__(self):
        return self.data.index

    def __float__(self):
        return float(self.data.index)

    def __str__(self):
        return self.data.item

    def __getitem__(self, item):
        if isinstance(item, int):
            result = enum(*self.data.items_tuple)
            result.data.index = item
            result.data.item = self.data.items_tuple[item]
            return result
        else:
            return getattr(self, item)

    def __getattr__(self, item):
        result = enum(*self.data.items_tuple)
        result.data.item = item
        result.data.index = self.data.items_tuple.index(item)
        return result

    def __cmp__(self, other):
        if isinstance(other, (float, int)) :
            return cmp(int(self), other)
        elif isinstance(other, (str, unicode)):
            return cmp(str(self), other)
        elif isinstance(other, Enum):
            return cmp(str(self), other)
        elif hasattr(other, "__int__") or hasattr(other, "__float__"):
            return cmp(int(self), int(other))
        return cmp(str(self), other)

    def __repr__(self):
        return 'enum({items})'.format(items=str(self.data.items_tuple)[1:-2])


class ArgWidget(object):
    type = None

    @classmethod
    def is_arg(cls, value):
        return isinstance(value, cls.type)

    @classmethod
    def instance(cls, value):
        if cls.is_arg(value):
            return cls()

    @property
    def arg(self):
        return self.get_arg()

    @arg.setter
    def arg(self, arg):
        if self.is_arg(arg):
            self.set_arg(arg)
        else:
            sys.stderr.write("{self}.arg type must be {self.__class__.__name__}".format(self=self))

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}()".format(self=self)


class Bool(QtGui.QCheckBox, ArgWidget):
    type = bool

    def __init__(self):
        QtGui.QCheckBox.__init__(self)
        self.argChanged = self.toggled
        self.get_arg = self.isChecked
        self.set_arg = self.setChecked


class Int(QtGui.QSpinBox, ArgWidget):
    type = int

    def __init__(self):
        QtGui.QSpinBox.__init__(self)
        self.setRange(-2147483648, 2147483647)
        self.argChanged = self.valueChanged
        self.get_arg = self.value
        self.set_arg = self.setValue

    def paintEvent(self, event):
        QtGui.QSpinBox.paintEvent(self, event)
        width = QtGui.QFontMetrics(self.font()).width(str(self.arg) + "0001")
        width = max(QtGui.QFontMetrics(self.font()).width("000000"), width)
        self.setFixedWidth(width)


class Float(QtGui.QDoubleSpinBox, ArgWidget):
    type = float

    def __init__(self):
        QtGui.QDoubleSpinBox.__init__(self)
        self.setRange(-2147483648, 2147483647)
        self.setDecimals(4)
        self.argChanged = self.valueChanged
        self.get_arg = self.value
        self.set_arg = self.setValue

    def paintEvent(self, event):
        QtGui.QDoubleSpinBox.paintEvent(self, event)
        width = QtGui.QFontMetrics(self.font()).width(str(self.arg) + "0001")
        width = max(QtGui.QFontMetrics(self.font()).width("000000"), width)
        self.setFixedWidth(width)


class String(QtGui.QLineEdit, ArgWidget):
    type = basestring

    def __init__(self):
        QtGui.QLineEdit.__init__(self)
        self.argChanged = self.textChanged
        self.get_arg = self.text
        self.set_arg = self.setText


class Enum(QtGui.QComboBox, ArgWidget):
    type = enum

    @classmethod
    def instance(cls, value):
        if cls.is_arg(value):
            return cls(*value.data.items_tuple)

    def __init__(self, *items):
        QtGui.QComboBox.__init__(self)
        self.items = items
        for item in items:
            self.addItem(item)
        self.argChanged = self.currentIndexChanged[str]

    @property
    def arg(self):
        return self.items[self.currentIndex()]

    @arg.setter
    def arg(self, arg):
        if isinstance(arg, int):
            if 0 <= arg <= len(self.items):
                self.setCurrentIndex(arg)
        elif arg in self.items:
            self.setCurrentIndex(self.items.index(arg))
        else:
            sys.stderr.write("{self}.arg must be a {self.type.__name__} in {self.items}".format(self=self))

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}({items})".format(self=self, items=str(self.items)[1:-2])

    def paintEvent(self, event):
        QtGui.QComboBox.paintEvent(self, event)
        width = QtGui.QFontMetrics(self.font()).width(str(self.arg) + "0001")
        width = max(QtGui.QFontMetrics(self.font()).width("000000"), width)
        self.setFixedWidth(width)


class Path(QtGui.QWidget, ArgWidget):
    type = basestring
    pattern = re.compile(r'[A-Z]:([\\/][^\\/:*?"<>|]+)*$')

    @classmethod
    def is_arg(cls, value):
        if String.is_arg(value):
            return bool(cls.pattern.match(value))
        return False

    @classmethod
    def instance(cls, value):
        if cls.is_arg(value):
            return cls(os.path.splitext(value)[-1])

    def __init__(self, ext):
        QtGui.QWidget.__init__(self)
        self.ext = ext
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QtGui.QLineEdit())
        self.layout().addWidget(QtGui.QPushButton("open"))
        self.file = QtGui.QFileDialog(self)
        self.layout().itemAt(1).widget().clicked.connect(self.file.show)
        self.file.fileSelected.connect(self.layout().itemAt(0).widget().setText)
        self.argChanged = self.layout().itemAt(0).widget().textChanged
        if ext:
            self.file.setNameFilter("file type(*%s)" % self.ext)
        else:
            self.file.setFileMode(self.file.Directory)
        self.get_arg = self.layout().itemAt(0).widget().text
        self.set_arg = self.layout().itemAt(0).widget().setText

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.ext}')".format(self=self)


class WidgetArray(QtGui.QWidget):
    widget = ArgWidget
    argChanged = QtCore.Signal(tuple)

    @classmethod
    def is_arg(cls, value):
        if isinstance(value, (tuple, list)):
            return all([cls.widget.is_arg(val) for val in value])
        else:
            return False

    @classmethod
    def instance(cls, value):
        if cls.is_arg(value):
            return cls(len(value))

    def __init__(self, number):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.widgets = [self.widget() for i in range(number)]
        for widget in self.widgets:
            self.layout().addWidget(widget)
            self.argChanged.connect(self.emit_arg)

    @property
    def arg(self):
        return tuple(self.layout().itemAt(index).widget().arg for index in range(self.layout().count()))

    @arg.setter
    def arg(self, arg):
        count = self.layout().count()
        if self.is_arg(arg) and len(arg) == count:
            for index, value in enumerate(arg):
                self.layout().itemAt(index).widget().arg = value
        else:
            error = "{self}.arg must be {number} {self.widget.__name__}"
            sys.stderr.write(error.format(self=self, number=self.layout().count()))

    def __repr__(self):
        return "{self.__class__.__name__}({number})".format(self=self, number=self.layout().count())

    def emit_arg(self):
        self.argChanged.emit(self.arg)


class BoolArray(WidgetArray):
    widget = Bool


class IntArray(WidgetArray):
    widget = Int


class FloatArray(WidgetArray):
    widget = Float


class PathArray(QtGui.QListWidget):
    argChanged = QtCore.Signal(list)

    @classmethod
    def is_arg(cls, value):
        if isinstance(value, (tuple, list)):
            return all([Path.is_arg(val) for val in value])
        else:
            return False

    @classmethod
    def instance(cls, value):
        if cls.is_arg(value):
            extensions = []
            for path in value:
                ext = os.path.splitext(path)[-1]
                if ext:
                    extensions.append(ext)
            return cls(*extensions)

    def __init__(self, *extensions):
        QtGui.QListWidget.__init__(self)
        self.extensions = extensions
        self.setAcceptDrops(True)
        self.paths = []
        self.menu = QtGui.QMenu(self)
        action = self.menu.addAction("clear")
        action.triggered.connect(self.clear)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        self.paths += [url.path().replace("\\", "/")[1:] for url in event.mimeData().urls()]
        self.arg = self.paths

    def clear(self):
        self.paths = []
        QtGui.QListWidget.clear(self)
        self.argChanged.emit(self.arg)

    @property
    def arg(self):
        return self.paths

    @arg.setter
    def arg(self, value):
        self.clear()
        if PathArray.is_arg(value):
            for path in value:
                is_file = self.extensions and (os.path.splitext(path)[-1] in self.extensions)
                is_dir = not self.extensions and (not os.path.splitext(path)[-1])
                if path not in self.paths and (is_file or is_dir):
                    self.paths.append(path)
                    self.addItem(path)
            self.argChanged.emit(self.arg)
        else:
            sys.stderr.write("{self}.arg must be [Path,Path……]".format(self=self))

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}({ext})".format(self=self, ext=str(self.extensions)[1:-2])

__all__ = [
    Bool,
    Int,
    Float,
    Path,
    Enum,
    String,
    BoolArray,
    IntArray,
    FloatArray,
    PathArray
]
