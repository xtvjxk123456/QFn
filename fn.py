# coding:utf-8
# path_array_arg, int_arg, int_array_arg, bool_arg, bool_array_arg

print u"加载数+1"


def man(name=u"小明", sex=u"男", height=150.0, body=None, save_file="D:/test.txt"):
    u"""
    :param name: 姓名。
    :param sex: 性别。
    :param height: 身高。
    :param body: 三围。
    :param save_file: 储存路径。
    没有实际功能的函数，仅测试用。
    """
    if body is None:
        body = [80.0, 56.0, 81.0]
    print "姓名：", name
    print "性别：", sex
    print "身高：", height
    print "三维：", body[0], body[1], body[2]
    print "记录路径：", save_file
