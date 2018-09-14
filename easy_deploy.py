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
直接运行 {info} 添加管理待操作的服务器

命令行参数:
按 {tab} 键自动显示所有的操作命令

Usage: {info} [options] [command] [keyword] [keyword] [keyword]..
{options}:
    -h,  --help                显示帮助
    push                       本地服务器推送文件到远程
    pull                       拉取远程服务器文件到本地
    run                        运行命令
    info                       显示操作服务器列表
{command}:
    local[:remote]             搭配push操作, 如果remote远程不指定,则默认推送到远程的用户目录
    remote[:local]             搭配pull操作, 如果local本地不指定，则默认拉取文件到当前目录
    'shell command'            搭配run操作, 运行的命令必须用英文单引号或双引号包括
{keyword}:                       
                               作用于包含指定关键字的服务器,不指定keyword则表示作用于所有服务器;
                               keyword输入可以不完整, 只要匹配到包含的服务器keyword即可生效作用;
                               可以指定多个keyword(空格隔开), 第三个及之后的传参都认为keyword;
                               pull操作必须指定关键字, 且匹配到的服务器只能一个
    """.format(options=color_str(Color.YELLOW, 'Options'),command=color_str(Color.YELLOW, 'Command'), keyword=color_str(Color.YELLOW, 'Keyword'), tab=color_str(Color.CYAN, 'Tab'), info=info))

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
        show_text = ("1. 新增服务器", "2.删除服务器", "3. 清除无法连接的服务器", "4. 修改服务器Keyword", "5. 按创建时间升序排列", "6. 按创建时间降序排列")
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
            index=loop_input_choice_number("请输入要改Keyword的服务器序号(回车退出): ", len(dp.server_list))
            print("选择的服务器info: ")
            print(dp.server_list[index - 1])
            new_keyword = input("请输入新的keyword信息(不能包含空格, 回车退出): ")
            if not new_keyword:
                break
            if " " in new_keyword:
                print("Keyword{0}包含{1}!\n".format(color_str(Color.RED, '不能'),color_str(Color.YELLOW, '空格')))
                break
            keyword_dict={'index':index-1, 'keyword':new_keyword}
            dp.modify_server_list(keyword_dict=keyword_dict)
        elif choice == 5:
            dp.modify_server_list(orderBy='asc')
        elif choice == 6:
            dp.modify_server_list(orderBy='desc')

        print("操作成功！")

def deal_select_server(select_server_list):

    select_server=set()
    for keyword_frag in select_server_list:
        frag_server=[]
        for server in dp.server_list:
            if keyword_frag in server.keyword:
                frag_server.append(server)
        if not frag_server:
            print("{} Keyword没匹配到服务器".format(color_str(Color.RED, keyword_frag)))
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

def push_file_controller(args_list):
    if not args_list:
        print(color_str(Color.RED, '传参有误!'))
        show_help()
    elif len(args_list) == 1:
        dp.test_server()

        upload_paths = args_list[0].split(':')
        local = upload_paths[0]
        remote = upload_paths[1] if len(upload_paths) == 2 else None
        dp.copy_file(local, remote)
    else:
        upload_paths = args_list[0].split(':')
        local = upload_paths[0]
        remote = upload_paths[1] if len(upload_paths) == 2 else None

        server_list=deal_select_server(args_list[1:])
        dp.copy_file(local, remote, server_list)

def pull_file_controller(args_list):
    if not args_list:
        print(color_str(Color.RED, '传参有误!'))
        show_help()
    elif len(args_list) == 1 and len(dp.server_list) == 1:
        dp.test_server()

        pull_paths = args_list[0].split(':')
        local = pull_paths[0]
        remote = pull_paths[1] if len(pull_paths) == 2 else None
        dp.copy_file(local, remote, reverse=True)
    else:
        pull_paths = args_list[0].split(':')
        local = pull_paths[0]
        remote = pull_paths[1] if len(pull_paths) == 2 else None

        server_list=deal_select_server(args_list[1:])
        
        if len(server_list) != 1:
            raise ValueError(color_str(Color.RED, '有且仅有一个服务器来传输文件'))
        dp.copy_file(local, remote, server_list, reverse=True)

def run_command_controller(args_list):
    if not args_list:
        print(color_str(Color.RED, '传参有误!'))
        show_help()
    elif len(args_list) == 1:
        dp.test_server()
        dp.run_command(args_list[0])
    else:
        server_list = deal_select_server(args_list[1:])
        dp.run_command(args_list[0], server_list)

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
    elif opts[0] == 'push':
        push_file_controller(opts[1:])
    elif opts[0] == 'pull':
        pull_file_controller(opts[1:])
    elif opts[0] == 'run':
        run_command_controller(opts[1:])
    elif opts[0] == 'info':
        dp.test_server()
        dp.print_server()
    else:
        print(color_str(Color.RED, '传参有误!'))
        show_help()