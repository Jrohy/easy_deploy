#! /usr/bin/python
# coding:utf-8
import os
import pexpect
import sys
import time
import threading
from multiprocessing import cpu_count, Pool
from fabric import Connection
from server import Server
from getopt import getopt,GetoptError
from utils import print_run_time, auto_save_data, color_str, check_ip, Color, generate_rsa

__author__ = 'Jrohy'

class Deployer:
    def _read_file_to_list(self, file_path):
        """
        配置文件每一行为一个服务器

        格式为 `user@ip port Timestamp`
        example: root@192.168.35.62 22 123242343
        """

        if not os.path.exists(file_path):
            path_tuple = os.path.split(file_path)
            if not os.path.exists(path_tuple[0]):
                os.makedirs(path_tuple[0])
            with open(file_path, 'w'):
                return []

        server_list=[]

        with open(file_path, 'r') as profile:
            content_list = profile.readlines()
            if content_list:
                for line in content_list:
                    
                    frag_info =  line.split("@")
                    user = frag_info[0]

                    frag_info = frag_info[1].split(" ")
                    if len(frag_info) != 4:
                        raise ValueError('配置格式不正确, 请执行:{}, 再重新运行'.format(color_str(Color.CYAN, 'rm -f ' + file_path)))
                    ip = frag_info[0]
                    port = frag_info[1]
                    remark = frag_info[2]
                    create_date = int(frag_info[3])

                    one_server = Server(ip, user=user, port=port, create_date=create_date, remark=remark)

                    server_list.append(one_server)

        return server_list
    
    def print_server(self):
        """
        打印这样的格式
        ====== 服务器列表 =====
        serverinfo....
        ==========================
        """
        key = "服务器列表"
        print()
        print("{:=^90}".format(" {0} ".format(key)))
        for index, server in enumerate(self.server_list):
            print("%d. %s" % (index + 1, server))
        index, condition = 0, 90 + len(key)
        while index < condition:
            print("{}".format("="), end="")
            index = index + 1
        print()
        print()

    def __init__(self, file_path):
        self._file_path = file_path
        self._server_list = self._read_file_to_list(file_path)

    @property
    def file_path(self):
        return self._file_path

    @property
    def server_list(self):
        return self._server_list

    # 不提供setter方法, 只能由modify_server_list方法修改
    # @server_list.setter
    # def server_list(self, value):
    #     self._server_list = value

    def test_server(self):
        """
        批量测试服务器连接性
        """
        for server in self.server_list:
            server.test_ssh()

    def _process_copy(self, server, scp_command, local_path, remote_path, reverse):
        if reverse:
            print("\n{0} {color_ip}:{local} to {remote}".format(color_str(Color.YELLOW, 'Downloading...'), local=local_path, remote=remote_path, color_ip=color_str(Color.FUCHSIA, server.ip)))
        else:
            print("\n{0} {local} to {color_ip}:{remote}".format(color_str(Color.YELLOW, 'Uploading...'), local=local_path, remote=remote_path, color_ip=color_str(Color.FUCHSIA, server.ip)))
        os.system(scp_command)

    @print_run_time('scp传输文件')
    def copy_file(self, local_path, remote_path=None, select_server=None, reverse=False):
        """
        scp方式复制文件，reverse=True表示从远程复制到本地
        """
        select_server = select_server if select_server else self.server_list

        pool = Pool(cpu_count() + 1)

        for server in select_server:
            if not server.is_ok:
                print("{} 无法连接, 直接跳过".format(color_str(Color.RED, server.ip)))
                continue

            # 如果remote_path为空则自动获取
            if not remote_path:
                if reverse:
                    remote_path = '.'
                else:
                    result = Connection(server.ip, server.user, server.port).run('echo $HOME', hide=True)
                    remote_path = result.stdout
            else:
                # 传输文件前先确保目录远程存在, 自动创建目录
                if len(remote_path) > 1 and not reverse:
                    Connection(server.ip, server.user, server.port).run('mkdir -p {}'.format(remote_path[:remote_path.rfind('/')]), hide=True)
                else:
                    os.system('mkdir -p {}'.format(remote_path[:remote_path.rfind('/')]))
            
            if reverse:
                scp_command = 'scp -P {server.port} -r {server.user}@{server.ip}:{local} {remote}'.format(server=server, local=local_path, remote=remote_path)
            else:
                scp_command = 'scp -P {server.port} -r {local} {server.user}@{server.ip}:{remote}'.format(server=server, local=local_path, remote=remote_path)

            if server.is_ok:
                print("\n多进程模式传输文件: %s" % color_str(Color.CYAN, local_path))
                pool.apply_async(self._process_copy, args=(server, scp_command, local_path, remote_path, reverse))       
        
        pool.close()
        #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        pool.join()

    def _thread_run(self, server, command):
        Connection(server.ip, server.user, server.port).run(command) 

    @print_run_time('运行命令')
    def run_command(self, command, select_server=None):
        """
        运行命令
        """
        select_server = select_server if select_server else self.server_list
        if 'tar ' in command:
            thread_list = []

            print("\n多线程运行命令: %s" % color_str(Color.CYAN, command))
            for server in select_server:
                if not server.is_ok:
                    print("{} 无法连接, 直接跳过".format(color_str(Color.RED, server.ip)))
                    continue
                thread = threading.Thread(target=self._thread_run, args=(server, command))
                thread_list.append(thread)
                thread.start()

            for thread in thread_list:
                thread.join()
        else:
            for server in select_server:
                print("\n{color_ip} ==> 运行结果:".format(color_ip=color_str(Color.FUCHSIA, server.ip)))
                Connection(server.ip, server.user, server.port).run(command) 
        
        
    @auto_save_data
    def modify_server_list(self, server=None, clean=False, delete_index=None, orderBy=None, remark_dict={}):
        if server:
            for exist_server in self.server_list:
                if exist_server.ip == server.ip and exist_server.is_ok:
                    print("{0} 已存在".format(color_str(Color.FUCHSIA, server.ip)))
                    return
            self._server_list.append(server)
        if remark_dict:
            print("remark_list: %s" % remark_dict)
            self._server_list[remark_dict.get('index')].remark = remark_dict.get('remark')
        if clean:
            self._server_list = list(filter(lambda server:server.is_ok, self.server_list))
        if delete_index:
            del self._server_list[delete_index]
        if orderBy == 'asc':
            self._server_list = sorted(self.server_list, key=lambda server:server.create_date)
        elif orderBy == 'desc':
            self._server_list = sorted(self.server_list, key=lambda server:server.create_date, reverse = True)

    def add_server(self, input_str):
        if not input_str:
            raise ValueError("无传参, 请重新输入")

        argv_list = input_str.split(" ")
        user, port = 'root', 22
        ip = argv_list[0]

        if not check_ip(ip):
            print("{0} 不是ip".format(color_str(Color.RED, ip)))
            return

        try:
            opts = getopt(argv_list[1:], "u:p:")
            for cmd, arg in opts[0]:
                if cmd in ("-u", "--username"):
                    user=arg
                elif cmd in ("-p", "--port"):
                    port=arg
        except GetoptError:
            print("输入错误, 输入格式为 ip [ -u ][ -p ]\nexample: 192.168.35.62 -u root -p 22")

        server=Server(ip, user=user, port=port)

        #测试能否连接
        server.test_ssh()
        #无法连接则复制密钥
        if not server.is_ok:
            generate_rsa()
            server.copy_ssh_id()

        self.modify_server_list(server=server)