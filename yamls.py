#coding:utf-8
import os
import yaml


class Yaml(object):
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
            yaml_dir = os.path.dirname(self.path)
            if not os.path.isdir(yaml_dir):
                os.makedirs(yaml_dir)
        self.data = data
        with open(self.path, 'w') as write:
            write.write(yaml.dump(data, default_flow_style=False))

    def reload(self):
        if os.path.isfile(self.path):
            with open(self.path, 'r') as read:
                self.data = yaml.load(read.read())
                return self.data

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.path}')".format(self=self)


class Yamls(object):
    __path__ = ""

    def __init__(self, path):
        self.__dict__["__path__"] = path

    def __contains__(self, item):
        if isinstance(item, Yaml):
            return self.__contains__(os.path.splitext(os.path.basename(item.path))[0])
        elif isinstance(item, Yamls):
            return self.__contains__(os.path.basename(item.__path__))
        elif hasattr(Yamls, item):
            return False
        elif os.path.isdir(self.__path__ + "/" + item):
            return True
        elif os.path.isfile(self.__path__ + "/" + item + ".yaml"):
            return True
        else:
            return False

    def __getattr__(self, attr):
        path = self.__path__ + "/" + attr + ".yaml"
        if os.path.isfile(path):
            self.__dict__[attr] = Yaml(path)
        else:
            self.__dict__[attr] = Yamls(self.__path__ + "/" + attr)
        return self.__dict__[attr]

    def __setattr__(self, attr, value):
        if hasattr(Yamls, attr):
            raise AttributeError("{self} attribute {attribute} cannot be changed".format(self=self, attribute=attr))
        if os.path.isdir(self.__path__ + "/" + attr):
            raise AttributeError("Yamls path {path} already exits".format(path=self.__path__ + "/" + attr))
        if not isinstance(self.__dict__.setdefault(attr), Yaml):
            self.__dict__[attr] = Yaml(self.__path__ + "/" + attr + ".yaml")
        self.__dict__[attr].write(value)

    def __getitem__(self, key):
        if hasattr(Yamls, key):
            raise KeyError("{self} has not key {key}".format(self=self, key=key))
        return getattr(self, key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __iter__(self):
        if os.path.isdir(self.__path__):
            for name in os.listdir(self.__path__):
                path = self.__path__ + "/" + name
                if os.path.isdir(path):
                    if hasattr(Yamls, name):
                        continue
                    if name not in self.__dict__:
                        self.__dict__[name] = Yamls(path)
                else:
                    name, ext = os.path.splitext(name)
                    if not ext == ".yaml":
                        continue
                    if hasattr(Yamls, name):
                        continue
                    if name not in self.__dict__:
                        self.__dict__[name] = Yaml(path)
                yield self.__dict__[name]

    def __repr__(self):
        return "{self.__module__}.{self.__class__.__name__}('{self.__path__}')".format(self=self)

