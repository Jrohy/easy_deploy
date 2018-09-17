#! /usr/bin/python3
# coding:utf-8
import re
import sys
import time
import os
import pexpect
from enum import Enum, unique
from functools import wraps

@unique
class Color(Enum):
    """
    终端显示颜色 枚举类
    """
   # 显示格式: \033[显示方式;前景色;背景色m
    # 只写一个字段表示前景色,背景色默认
    RED = '\033[31m'       # 红色
    GREEN = '\033[32m'     # 绿色
    YELLOW = '\033[33m'    # 黄色
    BLUE = '\033[34m'      # 蓝色
    FUCHSIA = '\033[35m'   # 紫红色
    CYAN = '\033[36m'      # 青蓝色
    WHITE = '\033[37m'     # 白色
    #: no color
    RESET = '\033[0m'      # 终端默认颜色

def color_str(color: Color, str: str) -> str:
    """
    返回有色字符串
    """
    return '{}{}{}'.format(
        color.value,
        str,
        Color.RESET.value
    )

def check_ip(ip):
    """
    判断字符串是否为ip
    """
    p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip):
        return True
    else:
        return False

def is_number(s):
    """
    判断是否为数字的函数
    """
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def auto_save_data(func):
    """
    自动保存数据的装饰器
    """  
    def wrapper(*args, **kw):  
        func(*args, **kw) 
        keyword_set = set()
        with open(args[0].file_path, 'w') as write_file:
            if not args[0].server_list:
                write_file.writelines()
            keyword_str = "	local keyword_array=("
            for server in args[0].server_list:
                write_file.writelines('{self.user}@{self.ip} {self.port} {self.keyword} {self.create_date}\n'.format(self=server))
                keyword_set.add(server.keyword)
            print("已自动保存配置文件到 ==> %s" % args[0].file_path)

        #修改命令行自动补全文件
        bash_completion_file = "/etc/bash_completion.d/easy_deploy.bash"

        if not os.path.exists(bash_completion_file):
            raise FileNotFoundError("命令行自动补全文件不存在: {} not found".format(color_str(Color.CYAN, bash_completion_file)))

        for index, keyword in enumerate(keyword_set):
            keyword_str = keyword_str + '"{}"'.format(keyword)
            if index+1 == len(keyword_set):
                keyword_str = keyword_str + ")"
            else:
                keyword_str = keyword_str + " "
        REPLACE_CMD = "sed -i 's/.*local keyword_array.*/{0}/g' {1}".format(keyword_str, bash_completion_file)
        os.system(REPLACE_CMD)
        print("如果有新增/修改keyword, 要马上在命令行使用(重开ssh会自动生效), 请手动执行命令:\n{}\n".format(color_str(Color.CYAN, "source " + bash_completion_file)))

    return wrapper

def print_run_time(msg=None):
    """
    打印函数执行时间的装饰器, msg为显示信息, 不传则显示函数名
    """  
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kw):  
            local_time = time.time()  
            func(*args, **kw)
            show_msg = msg if msg else ("函数 [%s]" % func.__name__)
            print('%s  耗时: %.2fs\n' % (show_msg ,time.time() - local_time))
        return wrapper
    return decorate

def generate_rsa(is_overwrite=False):
    """
    生成rsa公钥, 如果文件不存在或者文件为空则生成密钥
    is_overwrite 是否覆盖
    """
    rsa_path = os.environ['HOME'] + "/.ssh/id_rsa.pub"

    if is_overwrite or not os.path.exists(rsa_path) or not os.path.getsize(rsa_path):
        process = pexpect.spawn('ssh-keygen -t rsa')

        while True:
            # 待终端回显项, (?i)表示忽略大小写
            index = process.expect([
                '(?i)enter',
                '(?i)y/n',
                pexpect.TIMEOUT,
                pexpect.EOF
            ])
            if index == 0:
                process.sendline() #发送回车

            elif index == 1:
                process.sendline('y')

            elif index == 2:
                print("网络超时\n")
                break
            elif index == 3:
                print("密钥已生成\n")
                break