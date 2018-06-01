# _*_coding:utf-8 _*_
__author__ = 'david'
__date__ = '2018/5/29 16:55'

def split_nums(value):
    if len(value) == 2:
        return value[0], value[1]
    else:
        return value[0], 0

a = split_nums([2])[1]
print(a)