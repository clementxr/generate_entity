# -*- coding: utf-8 -*-
import cx_Oracle as oracle
import os
import sys
import convert_camel
import time

reload(sys)
sys.setdefaultencoding('utf8')
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

def openDatabase():
    # 读取文件，获取数据库配置
    filename = open("settings.txt", 'rb')
    lines = filename.read()
    global username
    for line in lines.split('\r'):
        if 'ip' in line:
            ip = line.split(':')[1]
        if 'port' in line:
            port = line.split(':')[1]
        if 'servicename' in line:
            servicename= line.split(':')[1]
        if 'username' in line:
            username = line.split(':')[1]
        if 'password' in line:
            password = line.split(':')[1]

    str="{}/{}@{}:{}/{}".format(username,password,ip,port,servicename)
    print str
    connect = oracle.connect(str)
    return connect

# 根据数据库用户名获取所有表名
def getTable(connect, username):
    cursor = connect.cursor()
    cursor.execute("select t1.TABLE_NAME,t2.COMMENTS from all_tables t1 ,user_tab_comments t2 WHERE t1.TABLE_NAME=t2.TABLE_NAME AND owner='%s' order by TABLE_NAME" % username)
    data = cursor.fetchall()
    cursor.close()
    return data

# 根据表名获取表的列名和注释
def getColumns(connect, tablename):
    cursor = connect.cursor()
    cursor.execute("select t1.column_name,t1.comments,t2.DATA_TYPE,t2.DATA_LENGTH,t2.NULLABLE from user_col_comments t1,user_tab_columns t2  WHERE t1.table_name = t2.table_name AND t1.column_name=t2.COLUMN_NAME AND t1.table_name = '%s'" % tablename)
    data = cursor.fetchall()
    cursor.close()
    return data


# 连接数据库
connect = openDatabase()
# 获取所有表
tables = getTable(connect, username.upper())
# 循环每个表
for table in tables:

    # 将字段名按驼峰命名法转换,首字母大写
    entityFileName = convert_camel.convert(table[0], '_',True)
    entity = open("entity/%sEntity.java" % entityFileName, 'w')
    entityComment = table[1]
    if entityComment is None:
        entityComment = entityFileName

    # 根据表名获取所有字段
    columns = getColumns(connect,table[0])

    lines = []
    types = {}
    getsetLines = []
    # 循环表内所有字段
    for i, column in enumerate(columns):

        # 将字段名按驼峰命名法转换,首字母小写
        columnName = convert_camel.convert(column[0], '_',False)
        # 字段注释
        comment = column[1]
        # 字段数据库类型
        columnType = column[2]
        # 将字段数据库类型转换为java类似
        # Number转换为Integer，DATE转为Date，其他为String
        if columnType == "NUMBER":
            columnType = "Integer"
        elif columnType == "DATE":
            columnType = "Date"
        else:
            columnType = "String"
        # 将类型放到类型的map中，后面需要添加引用
        types[columnType] = columnType
        # 为空会报错，所以注释为空时，将字段名作为注释
        if comment is None:
            comment = columnName
        # 一行注释
        commentLine = "\t/** " + comment + " */\n"
        # 一行字段
        line = "\tprivate " + columnType + " " + columnName + ";\n\n"
        # 需写的行
        lines.append(commentLine)
        lines.append(line)

        # 将字段名按驼峰命名法转换,首字母大写
        getsetColumn = convert_camel.convert(column[0], '_', True)

        #生成get
        getLine="\tpublic %s get%s() {\n\t\treturn %s;\n\t}\n\n" % (columnType, getsetColumn,columnName)
        getsetLines.append(getLine)
        # 生成set
        setLine = "\tpublic void set%s(%s %s) {\n\t\tthis.%s = %s;\n\t}\n\n" % (getsetColumn,columnType, columnName,columnName,columnName)
        getsetLines.append(setLine)

    # 如果有Date类型，添加引用
    if types.has_key("Date"):
        entity.writelines("import java.util.Date;\n\n")
    # Author注释
    entity.writelines("/**\n* <p>\n* "+entityComment+"Entity\n* </p>\n* @author: Auto Generate\n* @date: "+time.strftime('%Y-%m-%d',time.localtime(time.time()))+"\n*/\n")

    # 写类名
    entity.writelines("public class %sEntity {\n" % entityFileName)
    # 循环写入文件
    for line in lines:
        entity.writelines(line)
    for line in getsetLines:
        entity.writelines(line)
    entity.writelines("}")
    entity.close()
connect.close()
