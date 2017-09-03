def aa(bool_arg,
       bool_array_arg,
       int_arg,
       int_array_arg,
       float_arg,
       float_array_arg,
       string_arg,
       path_arg,
       enum_arg,
       path_array_arg):
    print bool_arg,bool_array_arg
    print int_arg,int_array_arg
    print float_arg,float_array_arg
    print string_arg,enum_arg,bool_arg,path_arg
    print path_array_arg


def bb(**kwargs):
    print "bb"
    print kwargs

print 1