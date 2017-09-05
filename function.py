# coding:utf-8
import os
import sys
import time
import socket
import traceback
import json
import inspect


class Log(object):
    u"""
    用来记录代码日志。
    """
    def __init__(self, path):
        u"""
        :param path: 日志路径。
        """
        self.path = path

    def __call__(self, *texts):
        u"""
        :param texts: 日志文本 <str>。
        记录日志文本到日志路径。
        """
        for text in texts:
            print text
        texts = [text + '\r\n' for text in texts]
        if not os.path.isfile(self.path):
            if not os.path.isdir(os.path.dirname(self.path)):
                os.makedirs(os.path.dirname(self.path))
        else:
            with open(self.path, 'r') as log:
                texts.extend(log.readlines()[:1000])
        with open(self.path, 'w') as log:
            log.writelines(texts)

    @property
    def time(self):
        u"""
        :return: 当前时间。
        """
        return time.strftime('%Y/%m/%d %H:%M')

    @property
    def error(self):
        u"""
        :return: 当前错误信息。
        """
        return traceback.format_exc().replace('\n', '\r\n')

    def open(self):
        u"""
        :return: 打开日志。
        """
        if os.path.isfile(self.path):
            os.startfile(self.path)

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Json(object):
    u"""
    用来读/写json文件。
    """
    def __init__(self, path):
        u"""
        :param path: json文件路径。
        """
        self.path = path
        self.__data = None

    def __nonzero__(self):
        return os.path.isfile(self.path)

    def read(self):
        u"""
        :return: json文件记录的数据
        """
        if self.__data is None:
            return self.reload()
        else:
            return self.__data

    def write(self, data):
        u"""
        将python数据写入json文件；
        :param data: python数据；
        """
        if not os.path.isfile(self.path):
            json_dir = os.path.dirname(self.path)
            if not os.path.isdir(json_dir):
                os.makedirs(json_dir)
        self.__data = data
        with open(self.path, 'w') as write:
            write.write(json.dumps(data))

    def reload(self):
        u"""
        当json文件以write函数之外的方式发生改变时，用reload来更新数据数据
        :return: json文件记录的数据
        """
        if os.path.isfile(self.path):
            with open(self.path, 'r') as read:
                self.__data = json.loads(read.read())
                return self.__data

    def delete(self):
        u"""
        删除json文件
        """
        if os.path.isfile(self.path):
            os.remove(self.path)

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Function(object):
    log = Log("{other}/data/log/{hostname}.log".format(other=os.path.dirname(__file__),
                                                       hostname=socket.gethostname()))

    def __init__(self, fn):
        if isinstance(fn, (str, unicode)):
            splits = fn.split(".")
            module_name = ".".join(splits[:-1])
            __import__(module_name)
            self.fn = getattr(sys.modules[module_name], splits[-1])
        elif isinstance(fn, Function):
            self.fn = fn.fn
        else:
            self.fn = fn
        self.name = self.fn.__name__
        self.module = self.fn.__module__
        self.fullName = self.module + "." + self.name
        self.json = Json("{other}/data/json/{hostname}/{name}.json".format(other=os.path.dirname(__file__),
                                                                           hostname=socket.gethostname(),
                                                                           name=self.fullName))
        args_pec = inspect.getargspec(self.fn)
        self.args = args_pec.args
        if args_pec.defaults:
            self.default = dict(zip(args_pec.args[-len(args_pec.defaults)-1:], args_pec.defaults))
            if not self.json:
                self.json.write(self.default)

    @property
    def kwargs(self):
        if isinstance(self.json.read(), dict):
            return {key: value for key, value in self.json.read().items() if key in self.args}
        else:
            return {}

    @kwargs.setter
    def kwargs(self, kwargs):
        if isinstance(kwargs, dict):
            self.json.write({key: value for key, value in kwargs.items() if key in self.args})

    def apply(self):
        self(**self.kwargs)

    def __call__(self, **kwargs):
        try:
            self.fn(**kwargs)
            self.kwargs = kwargs
        except:
            self.log(self.log.time, self.fullName, self.log.error)
            self.log.open()
            raise

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.fullName}')".format(self=self)

    def reload(self):
        reload(sys.modules[self.module])
        self.fn = getattr(sys.modules[self.module], self.name)
