#! /usr/bin/python
# coding:utf-8
import re
import time
import pexpect
import sys
import os
from getpass import getpass
from utils import color_str, Color, print_run_time

__author__ = 'Jrohy'

class Server:
    def __init__(self, ip, *, user='root', port=22, create_date=None, remark=None):
        self.ip = ip
        self.user = user
        self.port = port
        self.create_date = int(time.time()) if create_date == None else create_date
        self.remark = remark if remark else ip

    # print一个实例打印的字符串
    def __str__(self):
        format_date = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(self.create_date)))
        color_status = color_str(Color.GREEN if self.is_ok else Color.RED, self.is_ok)
        return "{info}, remark:{color_remark}, status: {color_status},  createDate:{format_date}\n".format(self=self,color_remark=color_str(Color.CYAN, self.remark), info=self._get_server_command(True), color_status=color_status, format_date=format_date)

    # 直接调用实例和打印一个实例显示的字符串一样
    def __repr__ (self):
        return self.__str__

    def _get_server_command(self, with_color=False):
        if with_color:
            return '{self.user}@{color_ip} -p {self.port}'.format(self=self, color_ip=color_str(Color.FUCHSIA, self.ip))
        else:
            return '{self.user}@{self.ip} -p {self.port}'.format(self=self)

    @print_run_time('测试ssh连接性')
    def test_ssh(self):
        """
        测试能否连接到服务器
        """
        # 调试模式,设置超时
        # process = pexpect.spawnu('ssh %s' % self._get_server_command(), timeout=10, logfile=sys.stdout)
        process = pexpect.spawnu('ssh %s' % self._get_server_command(), timeout=10)
        response = [
                '(?i)yes/no',
                self.user,
                '(?i)Permission denied',
                '(?i)password',
                '(?i)failed',
                '(?i)not known',
                '(?i)Connection refused',
                pexpect.TIMEOUT,
                pexpect.EOF
            ]
        while True:
            # 待终端回显项, (?i)表示忽略大小写
            index = process.expect(response)
            # print("index ==> %d" % index)
            if index == 0:
                process.sendline('yes')
            
            elif index == 1:
                #发送结束登陆状态
                process.sendcontrol('d') 
                # process.sendeof()

            elif index == 2 or index == 3 or index == 4 or index == 5 or index == 6 or index == 7:
                self.is_ok = False
                print("{0} test {1}".format(color_str(Color.FUCHSIA, self.ip), color_str(Color.RED, 'fail')))
                break

            else:
                self.is_ok = True
                print("{0} test {1}".format(color_str(Color.FUCHSIA, self.ip), color_str(Color.GREEN, 'success')))
                break

    @print_run_time('复制密钥')
    def copy_ssh_id(self):
        """
        复制本机密钥到远程服务器
        """
        process = pexpect.spawnu('ssh-copy-id %s' % self._get_server_command(), timeout=15)
        # 调试模式
        # process = pexpect.spawnu('ssh-copy-id %s' % self._get_server_command(), timeout=15, logfile=sys.stdout)

        while True:
            # 待终端回显项, (?i)表示忽略大小写
            index = process.expect([
                '(?i)Host key verification failed',
                '(?i)added',
                '(?i)password',
                '(?i)already exist',
                '(?i)yes/no',
                '(?i)not known',
                pexpect.TIMEOUT,
                pexpect.EOF
            ])
            # print("index ==> %d" % index)

            if index == 0:
                print("Host key verification {}, auto remove {} in ~/.ssh/known_hosts".format(color_str(Color.RED, 'fail'), color_str(Color.FUCHSIA, self.ip)))
                os.system("sed -i '/{}/d' ~/.ssh/known_hosts".format(self.ip))
                #递归处理
                self.copy_ssh_id()
                break

            elif index == 1:
                print("{0} ==> {1}".format(color_str(Color.GREEN, '已复制密钥到'), color_str(Color.FUCHSIA, self.ip)))
                self.is_ok=True
                break

            elif index == 2:
                password=getpass("please input password: ")
                process.sendline(password)

            elif index == 3:
                print("{0} ==> {1}".format(color_str(Color.YELLOW, '密钥已存在'), color_str(Color.FUCHSIA, self.ip)))
                self.is_ok=True
                break

            elif index == 4:
                process.sendline("yes")

            elif index == 5:
                print("{0}".format(color_str(Color.RED, 'Name or service not known!')))
                self.is_ok = False
                break

            elif index == 6:
                print("{0}".format(color_str(Color.RED, '网络超时')))
                self.is_ok = False
                break

            else:
                print("{0}".format(color_str(Color.RED, 'copy ssh-id Fail!')))
                self.is_ok = False
                break