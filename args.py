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
import sys


class Bool(QtGui.QCheckBox):
    def __init__(self):
        QtGui.QCheckBox.__init__(self)
        self.argChanged = self.toggled

    @property
    def arg(self):
        return self.isChecked()

    @arg.setter
    def arg(self, value):
        if isinstance(value, bool):
            self.setChecked(value)
        else:
            sys.stderr.write("{self}.arg must be bool".format(self=self))

    def __repr__(self):
        return "{self.__class__.__name__}()".format(self=self)


class BoolArray(QtGui.QWidget):
    argChanged = QtCore.Signal(list)

    def __init__(self, *texts):
        u"""
        :param texts: 每勾选框文本<tuple(str,str……)>
        """
        QtGui.QWidget.__init__(self)
        self.texts = list(texts)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        def emit_args():
            self.argChanged.emit(self.arg)

        for index, text in enumerate(self.texts):
            self.layout().addWidget(QtGui.QCheckBox(text))
            self.layout().itemAt(index).widget().toggled.connect(emit_args)

    @property
    def arg(self):
        return [self.layout().itemAt(index).widget().isChecked() for index in range(self.layout().count())]

    @arg.setter
    def arg(self, value):
        if hasattr(value, "__iter__"):
            value = [i for i in value if isinstance(i, bool)]
            if len(value) == self.layout().count():
                for index in range(self.layout().count()):
                    self.layout().itemAt(index).widget().setChecked(value[index])
                return
        warnings = "{self}.arg must be {length} bool list".format(self=self, length=self.layout().count())
        sys.stderr.write(warnings)

    def __repr__(self):
        return "{self.__class__.__name__}({labels})".format(self=self, labels=repr(self.texts)[1:-1])


class Int(QtGui.QSpinBox):

    def __init__(self, min_value=-2147483648, max_value=2147483647):
        u"""
        :param min_value: 最小值
        :param max_value: 最大值
        """
        QtGui.QSpinBox.__init__(self)
        self.setRange(max(min_value, -2147483648), min(max_value, 2147483647))
        self.argChanged = self.valueChanged
        self.setFixedWidth(QtGui.QFontMetrics(self.font()).width(str(self.value()) + "000"))

    @property
    def arg(self):
        return self.value()

    @arg.setter
    def arg(self, value):
        if isinstance(value, int):
            self.setValue(value)
        else:
            sys.stderr.write("{self}.arg must be int".format(self=self))

    def __repr__(self):
        if self.maximum() == 2147483647 and self.minimum() == -2147483648:
            return "{self.__class__.__name__}()".format(self=self)
        return "{self.__class__.__name__}({min},{max})".format(self=self, min=self.minimum(), max=self.maximum())

    def paintEvent(self, event):
        QtGui.QSpinBox.paintEvent(self, event)
        width = QtGui.QFontMetrics(self.font()).width(str(self.value()) + "000")
        width = max(QtGui.QFontMetrics(self.font()).width("0000000"), width)
        self.setFixedWidth(width)


class IntArray(QtGui.QWidget):
    argChanged = QtCore.Signal(list)

    def __init__(self, labels, min_value=-2147483648, max_value=2147483647):
        u"""
        :param labels: 每整数输入框标签<tuple(str,str……)>
        :param min_value: 最小值
        :param max_value: 最大值
        """
        QtGui.QWidget.__init__(self)
        self.labels = labels
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        def emit_args():
            self.argChanged.emit(self.arg)

        for index, label in enumerate(labels):
            self.layout().addWidget(QtGui.QLabel(label+": "))
            self.layout().addWidget(Int(min_value, max_value))
            self.layout().itemAt(index * 2 + 1).widget().valueChanged.connect(emit_args)

    @property
    def arg(self):
        return [self.layout().itemAt(index * 2 + 1).widget().value() for index in range(self.layout().count()/2)]

    @arg.setter
    def arg(self, value):
        if hasattr(value, "__iter__"):
            value = [i for i in value if isinstance(i, int)]
            if len(value) == self.layout().count() / 2:
                for index in range(self.layout().count() / 2):
                    self.layout().itemAt(index * 2 + 1).widget().arg = value[index]
                return
        warnings = "{self}.arg must be {length} int".format(self=self, length=self.layout().count()/2)
        sys.stderr.write(warnings)

    def __repr__(self):
        min_value = self.layout().itemAt(1).widget().minimum()
        max_value = self.layout().itemAt(1).widget().maximum()
        if max_value == 2147483647 and min_value == -2147483648:
            return "{self.__class__.__name__}({self.labels})".format(self=self)
        return "{self.__class__.__name__}({self.labels},{min},{max})".format(self=self, min=min_value, max=max_value)


class Float(QtGui.QDoubleSpinBox):

    def __init__(self, min_value=-2147483648, max_value=2147483647):
        u"""
        :param min_value: 最小值
        :param max_value: 最大值
        """
        QtGui.QDoubleSpinBox.__init__(self)
        self.setRange(max(min_value, -2147483648), min(max_value, 2147483647))
        self.argChanged = self.valueChanged
        self.setFixedWidth(QtGui.QFontMetrics(self.font()).width(str(self.value()) + "0000"))

    @property
    def arg(self):
        return self.value()

    @arg.setter
    def arg(self, value):
        if isinstance(value, float):
            self.setValue(value)
        else:
            sys.stderr.write("{self}.arg must be float".format(self=self))

    def __repr__(self):
        if self.maximum() == 2147483647 and self.minimum() == -2147483648:
            return "{self.__class__.__name__}()".format(self=self)
        return "{self.__class__.__name__}({min},{max})".format(self=self, min=self.minimum(), max=self.maximum())

    def paintEvent(self, event):
        QtGui.QDoubleSpinBox.paintEvent(self, event)
        width = QtGui.QFontMetrics(self.font()).width(str(self.value()) + "0000")
        width = max(QtGui.QFontMetrics(self.font()).width("0000000"), width)
        self.setFixedWidth(width)


class FloatArray(QtGui.QWidget):
    argChanged = QtCore.Signal(list)

    def __init__(self, labels, min_value=-2147483648, max_value=2147483647):
        u"""
        :param labels: 每整数输入框标签<tuple(str,str……)>
        :param min_value: 最小值
        :param max_value: 最大值
        """
        QtGui.QWidget.__init__(self)
        self.labels = labels
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        def emit_args():
            self.argChanged.emit(self.arg)

        for index, label in enumerate(labels):
            self.layout().addWidget(QtGui.QLabel(label+": "))
            self.layout().addWidget(Float(min_value, max_value))
            self.layout().itemAt(index * 2 + 1).widget().valueChanged.connect(emit_args)

    @property
    def arg(self):
        return [self.layout().itemAt(index * 2 + 1).widget().value() for index in range(self.layout().count()/2)]

    @arg.setter
    def arg(self, value):
        if hasattr(value, "__iter__"):
            value = [i for i in value if isinstance(i, float)]
            if len(value) == self.layout().count() / 2:
                for index in range(self.layout().count() / 2):
                    self.layout().itemAt(index * 2 + 1).widget().arg = value[index]
                return
        warnings = "{self}.arg must be {length} float".format(self=self, length=self.layout().count()/2)
        sys.stderr.write(warnings)

    def __repr__(self):
        min_value = self.layout().itemAt(1).widget().minimum()
        max_value = self.layout().itemAt(1).widget().maximum()
        if max_value == 2147483647 and min_value == -2147483648:
            return "{self.__class__.__name__}({self.labels})".format(self=self)
        return "{self.__class__.__name__}({self.labels},{min},{max})".format(self=self, min=min_value, max=max_value)


class String(QtGui.QLineEdit):
    def __init__(self):
        QtGui.QLineEdit.__init__(self)
        self.argChanged = self.textChanged

    @property
    def arg(self):
        return self.text()

    @arg.setter
    def arg(self, value):
        if isinstance(value, (str, unicode)):
            self.setText(value)
        else:
            sys.stderr.write("{self}.arg must be str".format(self=self))

    def __repr__(self):
        return "{self.__class__.__name__}()".format(self=self)


class Enum(QtGui.QComboBox):
    def __init__(self, *texts):
        QtGui.QComboBox.__init__(self)
        self.texts = texts
        for text in texts:
            self.addItem(text)
        self.argChanged = self.currentIndexChanged[str]

    def paintEvent(self, event):
        QtGui.QComboBox.paintEvent(self, event)
        self.setFixedWidth(QtGui.QFontMetrics(self.font()).width(self.arg+"0000"))

    @property
    def arg(self):
        return self.itemText(self.currentIndex())

    @arg.setter
    def arg(self, value):
        if value in self.texts:
            self.setCurrentIndex(self.findText(value))
        else:
            sys.stderr.write("{self}.arg must be in {self.texts}".format(self=self))

    def __repr__(self):
        return "{self.__class__.__name__}({texts})".format(self=self, texts=repr(self.texts)[1:-1])


class Path(QtGui.QWidget):
    def __init__(self, ext=""):
        u"""
        :param ext: 文件扩展名
        空字符串:只打开文件夹
        *：打开任意扩展名的文件
        str: 打开指定扩展名的文件
        list[str, str……]：打开列表内所有扩展名的文件
        """
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
            if ext == "*":
                file_filter = "All File(*)"
            elif isinstance(ext, list):
                file_filter = "file types(%s)" % " ".join(["*."+e for e in ext])
            else:
                file_filter = "file type(*.%s)" % ext
            self.args = [ext]
            self.file.setNameFilter(file_filter)
        else:
            self.file.setFileMode(self.file.Directory)

    @property
    def arg(self):
        return self.layout().itemAt(0).widget().text().replace('\\', '/')

    @arg.setter
    def arg(self, value):
        if isinstance(value, (str, unicode)):
            self.layout().itemAt(0).widget().setText(value)
        else:
            sys.stderr.write("{self}.arg must be str".format(self=self))

    def __repr__(self):
        if not self.ext:
            return "{self.__class__.__name__}()".format(self=self)
        elif isinstance(self.ext, list):
            return "{self.__class__.__name__}({self.ext})".format(self=self)
        else:
            return "{self.__class__.__name__}('{self.ext}')".format(self=self)


class PathArray(QtGui.QListWidget):
    argChanged = QtCore.Signal(list)

    def __init__(self, pattern=""):
        u"""
        路径列表窗<list/str>
        :param pattern: 正则表达式(文件命名规则)
        """
        QtGui.QListWidget.__init__(self)
        self.pattern = re.compile(pattern)
        self.setAcceptDrops(True)
        self.paths = []
        self.menu = QtGui.QMenu(self)
        action = self.menu.addAction("clear")
        action.triggered.connect(self.clear)

    def contextMenuEvent(self, event):
        u"""
        右击事件，显示右键菜单
        """
        self.menu.exec_(event.globalPos())

    def dragEnterEvent(self, event):
        u"""
        允许携带路径信息的QDrag触发拖拽事件；
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        u"""
        鼠标在组件上移动时,不再进行可触发拖拽事件的判断；
        """
        pass

    def dropEvent(self, event):
        u"""
        拖拽事件，添加QDrag携带的路径到路径列表框；
        """
        self.paths += [url.path().replace("\\", "/")[1:] for url in event.mimeData().urls()]
        self.arg = self.paths

    def clear(self):
        """
        清空路径列表；
        """
        self.paths = []
        QtGui.QListWidget.clear(self)
        self.argChanged.emit(self.arg)

    @property
    def arg(self):
        return self.paths

    @arg.setter
    def arg(self, value):
        self.clear()
        if hasattr(value, "__iter__"):
            for path in value:
                if isinstance(path, (str, unicode)):

                    if path not in self.paths:
                        self.paths.append(path)
                        self.addItem(path)
                        print path
                        print "path"
            self.argChanged.emit(self.arg)
        else:
            sys.stderr.write("{self}.arg must be [str,str……]".format(self=self))

    def __repr__(self):
        if self.pattern.pattern:
            return "{self.__class__.__name__}('{self.pattern.pattern}')".format(self=self)
        else:
            return "{self.__class__.__name__}()".format(self=self)
