#coding:utf-8
import os
import sys
import time
import socket
import traceback
import json
import inspect


class Log(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, *args):
        for arg in args:
            print arg
        lines = [line + '\r\n' for line in args]
        if not os.path.isfile(self.path):
            if not os.path.isdir(os.path.dirname(self.path)):
                os.makedirs(os.path.dirname(self.path))
        else:
            with open(self.path, 'r') as log:
                lines.extend(log.readlines()[:1000])
        with open(self.path, 'w') as log:
            log.writelines(lines)

    @property
    def time(self):
        return time.strftime('%Y/%m/%d %H:%M')

    @property
    def error(self):
        return traceback.format_exc().replace('\n', '\r\n')

    def open(self):
        if os.path.isfile(self.path):
            os.startfile(self.path)

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Json(object):
    def __init__(self, path):
        self.path = path
        self.data = None

    def __nonzero__(self):
        return os.path.isfile(self.path)

    def read(self):
        if self.data is None:
            return self.reload()
        else:
            return self.data

    def write(self, data):
        if not os.path.isfile(self.path):
            json_dir = os.path.dirname(self.path)
            if not os.path.isdir(json_dir):
                os.makedirs(json_dir)
        self.data = data
        with open(self.path, 'w') as write:
            write.write(json.dumps(data))

    def reload(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as read:
                self.data = json.loads(read.read())
                return self.data

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
