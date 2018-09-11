# -*- coding: utf-8 -*-

def convert(one_string,space_character,first_upper):
    string_list = str(one_string).split(space_character)
    if first_upper:
        first = string_list[0].capitalize()
    else:
        first = string_list[0].lower()
    n = len(string_list )#取出数组长度
    others = [string_list[i].capitalize() for i in range(1,n)]
    #除了第一个元素依次执行首字母大写
    prehump = [first]+others#用“+”实现数组合并
    hump_string = ''.join(prehump)
    return hump_string

if __name__=='__main__':

    print "the string is:ab-cd-ef-gh"
    print "convert to hump:"
    print convert("ab-cd-ef-gh","-",False)
    print convert("FM_DAY_FLIGHT", "_",True)