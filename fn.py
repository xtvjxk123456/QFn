# coding:utf-8
# 测试用函数，无意义。
# man: String, Enum, Float, FloatArray, Path
# more: pathArray, Int, IntArray, Bool, BoolArray

print u"加载数+1"


def man(name="lisa", sex=u"man", height=150.0, body=(80.0, 50.0, 80.0), save_file="D:/test.txt"):
    u"""
    :param name: 姓名。
    :param sex: 性别。
    :param height: 身高。
    :param body: 三围。
    :param save_file: 储存路径。
    没有实际功能的函数，仅测试用。
    """
    print u"姓名：", name
    print u"性别：", sex
    print u"身高：", height
    print u"三维：", body[0], body[1], body[2]
    print u"记录路径：", save_file


def more(**kwargs):
    for key, value in kwargs.items():
        print key, value
