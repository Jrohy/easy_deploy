#!/bin/bash

#######color code########
RED="31m"      # Error message
GREEN="32m"    # Success message
YELLOW="33m"   # Warning message
BLUE="36m"     # Info message

colorEcho(){
    COLOR=$1
    echo -e "\033[${COLOR}${@:2}\033[0m"
}

#检查是否为Root
[ $(id -u) != "0" ] && { colorEcho ${RED} "Error: You must be root to run this script"; exit 1; }

#检查系统信息
if [ -f /etc/redhat-release ];then
        OS='CentOS'
    elif [ ! -z "`cat /etc/issue | grep bian`" ];then
        OS='Debian'
    elif [ ! -z "`cat /etc/issue | grep Ubuntu`" ];then
        OS='Ubuntu'
    else
        colorEcho ${RED} "Not support OS, Please reinstall OS and retry!"
        exit 1
fi

#卸载
if [[ $1 == '--uninstall' ]];then
    [[ -e /usr/local/bin/easy_deploy ]] && rm -f /usr/local/bin/easy_deploy
    [[ -e /etc/bash_completion.d/easy_deploy.bash ]] && rm -f /etc/bash_completion.d/easy_deploy.bash
    [[ -e /usr/local/easy_deploy/ ]] && rm -rf /usr/local/easy_deploy
    #删除easy_deploy环境变量
    sed -i '/easy_deploy/d' ~/.bashrc
    source ~/.bashrc
    colorEcho ${GREEN} "uninstall success!"
    exit 0
fi

#安装依赖
if [[ ${OS} == 'CentOS' ]];then
    yum install epel-release curl wget unzip git -y
    yum install python34 -y
else
    apt-get update
    apt-get install curl unzip git wget python3 -y
fi

# 安装最新版pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
rm -f get-pip.py

# 安装 pip依赖
pip install fabric pexpect

cd /usr/local/

if [[ -e easy_deploy && -e easy_deploy/.git ]];then
    cd easy_deploy
    git reset --hard && git pull
else
    git clone https://github.com/Jrohy/easy_deploy
    cd easy_deploy
fi

chmod +x easy_deploy
cp -f easy_deploy /usr/local/bin/

cp -f easy_deploy.bash /etc/bash_completion.d/
source /etc/bash_completion.d/easy_deploy.bash

#加入环境变量
[[ -z $(grep easy_deploy.bash ~/.bashrc) ]] && echo "source /etc/bash_completion.d/easy_deploy.bash" >> ~/.bashrc && source ~/.bashrc

#解决Python3中文显示问题
[[ -z $(grep PYTHONIOENCODING=utf-8 ~/.bashrc) ]] && echo "export PYTHONIOENCODING=utf-8" >> ~/.bashrc && source ~/.bashrc

colorEcho ${GREEN} "Install success!"
