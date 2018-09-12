#! /usr/bin/python3
# coding:utf-8
import os
import sys
from utils import is_number, color_str, Color
from getopt import getopt,GetoptError
from deployer import Deployer

__author__ = 'Jrohy'

def show_help():
    if '.py' in sys.argv[0]:
        info = 'python3 ' + sys.argv[0]
    else:
        info = sys.argv[0]
    print(
    """
Usage: {info} [options] [command][selectServer]
Options:
    -h,  --help                output usage information
    put                        batch upload file 
    run                        batch run command
    info                       show server info
Commands:
    local[:remote]             for put options to upload file, no ':remote' mean upload to target server '~' path. you can use '~' path
    "shell command"                     for run options to run command , must wrap with " or '
SelectServer:
    93,62                      remark contain '93' or '62' server can effect
Example:
    {info} put ~/23.tar   #upload ~/23.tar file to target server '~' path
    {info} put /home/v2ray:~/great/  #upload /home/v2ray folder to ~/great/ path
    {info} put /home/v2ray:~/great/ 打包  #upload /home/v2ray folder to ~/great/ path in remark contain '打包' server
    {info} run 'date'     #batch run command to show server time
    {info} run 'tar xzvf v2ray.tar.gz && cd v2ray'     #batch extract v2ray.tar.gz and cd to v2ray
    {info} run 'tar xzvf v2ray.tar.gz && cd v2ray' 93,32   #batch extract v2ray.tar.gz and cd to v2ray in remark contain '93' or '32' server 
    """.format(info=info))

def loop_input_choice_number(input_tip, number_max):
    """
    循环输入选择的序号,直到符合规定为止
    """
    while True:
        choice = input(input_tip)
        if not choice:
            sys.exit(0)
        if is_number(choice):
            choice = int(choice)
        else:
            print("输入有误,请重新输入")
            continue
        if (choice <= number_max and choice > 0):
            return choice
        else:
            print("输入有误，请重新输入")

def loop_manage_server():
    dp.test_server()
    while True:
        dp.print_server()
        show_text = ("1. 新增服务器", "2.删除服务器", "3. 清除无法连接的服务器", "4. 修改服务器备注", "5. 按创建时间升序排列", "6. 按创建时间降序排列")
        for index, text in enumerate(show_text): 
            if index % 2 == 0:
                print('{:<25}'.format(text), end="")   
            else:
                print(text)
        
        choice = loop_input_choice_number("\n请输入功能序号(回车退出):", len(show_text))
        
        if choice == 1:
            print("输入格式为 ip [ -u ][ -p ]\nexample: 192.168.35.62 -u root -p 22, 其中-u, -p可选, 默认值root, 22\n")
            info = input("请输入服务器信息: ")
            if info:
                dp.add_server(info)
            else:
                print("输入为空!")
        elif choice == 2:
            delete_index=loop_input_choice_number("请输入要删除的服务器序号(回车退出): ", len(dp.server_list))
            dp.modify_server_list(delete_index=delete_index-1)
        elif choice == 3:
            dp.modify_server_list(clean=True)
        elif choice == 4:
            index=loop_input_choice_number("请输入要改备注的服务器序号(回车退出): ", len(dp.server_list))
            print("选择的服务器info: ")
            print(dp.server_list[index - 1])
            new_remark = input("请输入新的remark信息(不能包含空格, 回车退出): ")
            if not new_remark:
                break
            if " " in new_remark:
                print("备注{0}包含{1}!\n".format(color_str(Color.RED, '不能'),color_str(Color.YELLOW, '空格')))
                break
            remark_dict={'index':index-1, 'remark':new_remark}
            dp.modify_server_list(remark_dict=remark_dict)
        elif choice == 5:
            dp.modify_server_list(orderBy='asc')
        elif choice == 6:
            dp.modify_server_list(orderBy='desc')

        print("操作成功！")

def deal_select_server(select_server_str):
    select_server_list = select_server_str.split(',')
    
    select_server=set()
    for remark_frag in select_server_list:
        frag_server=[]
        for server in dp.server_list:
            if remark_frag in server.remark:
                frag_server.append(server)
        if not frag_server:
            print("{} 备注没匹配到服务器".format(color_str(Color.RED, remark_frag)))
        else:
            #集合的并集
            select_server = select_server | set(frag_server)
        
    if select_server:
        server_list = list(select_server)
        print("\n匹配到的服务器列表: {}\n\n".format(color_str(Color.FUCHSIA, [x.ip for x in server_list])), end="")
    else:
        server_list = dp.server_list

    # 测试服务器连接性
    for server in server_list:
        server.test_ssh()
    return server_list

def put_file_controller(args_list):
    if not args_list:
        print(color_str(Color.RED, '传参有误!'))
        show_help()
    elif len(args_list) == 1:
        dp.test_server()

        upload_paths = args_list[0].split(':')
        local = upload_paths[0]
        remote = upload_paths[1] if len(upload_paths) == 2 else None
        dp.copy_file(local, remote)
    elif len(args_list) == 2:
        upload_paths = args_list[0].split(':')
        local = upload_paths[0]
        remote = upload_paths[1] if len(upload_paths) == 2 else None

        select_server = args_list[1]
        server_list=deal_select_server(select_server)
        
        dp.copy_file(local, remote, server_list)

    else:
        print(color_str(Color.RED, '传参有误!'))
        show_help()

def run_command_controller(args_list):
    if not args_list:
        print(color_str(Color.RED, '传参有误!'))
        show_help()
    elif len(args_list) == 2:
        server_list = deal_select_server(args_list[1])
        dp.run_command(args_list[0], server_list)
    elif len(args_list) == 1:
        dp.test_server()
        dp.run_command(args_list[0])

if __name__=='__main__':
    if '-h' in sys.argv or '--help' in sys.argv:
        show_help()
        sys.exit(0)

    print(color_str(Color.YELLOW, "loading profile ing...\n"))

    conf_path=os.environ['HOME'] + "/.ssh/auto_password.conf"
    dp=Deployer(conf_path)

    print('read profile {}\n'.format(color_str(Color.GREEN, "success")))

    opts = sys.argv[1:]

    if not opts:
        loop_manage_server()
    elif opts[0] == 'put':
        put_file_controller(opts[1:])
    elif opts[0] == 'run':
        run_command_controller(opts[1:])
    elif opts[0] == 'info':
        dp.test_server()
        dp.print_server()
    else:
        print(color_str(Color.RED, '传参有误!'))
        show_help()