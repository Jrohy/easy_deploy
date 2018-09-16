# easy_deploy
多服务器自动免密管理, 多进程批量传文件、执行命令 脚本  

### 安装 & 更新  
`source <(curl -sL https://git.io/fA128)`

### 卸载  
`source <(curl -sL https://git.io/fA128) --uninstall`

### 帮助
- 管理待操作的服务器  
直接输入`easy_deploy`来管理所有要操作的服务器

- 命令行参数  
    ```
    按 Tab 键自动显示所有的操作命令


    Usage: easy_deploy [options] [command] [keyword] [keyword] [keyword]..
    options:
        -h,  --help                显示帮助
        push                       本地服务器推送文件到远程
        pull                       拉取远程服务器文件到本地
        run                        运行命令
        info                       显示操作服务器列表
    command:
        local[:remote]             搭配push操作, 如果remote远程不指定,则默认推送到远程的用户目录
        remote[:local]             搭配pull操作, 如果local本地不指定，则默认拉取文件到当前目录
        'shell command'            搭配run操作, 运行的命令必须用英文单引号或双引号包括
    keyword:                       
                                   作用于包含指定关键字的服务器,不指定keyword则表示作用于所有服务器;
                                   keyword输入可以不完整, 只要匹配到包含的服务器keyword即可生效作用;
                                   可以指定多个keyword(空格隔开), 第三个及之后的传参都认为keyword;
                                   pull操作必须指定关键字, 且匹配到的服务器只能一个
    ```

### BASED ON
[Fabric 2.0](https://github.com/fabric/fabric/)  
[Pexpect](https://github.com/pexpect/pexpect)