#coding:utf-8
from yamls import Yamls as _Yamls
from function import Function
import os as _os

default = _Yamls(_os.path.dirname(__file__)+"/data/yaml")

__all__ = ["default", "Function"]
