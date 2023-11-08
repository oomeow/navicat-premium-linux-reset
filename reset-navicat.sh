#!/bin/bash

# python 命令路径
PYTHON_BIN_PATH=""

# 错误信息显示
message() {
    TITLE="Cannot start reset Navicat"
    if [ -n "$(command -v zenity)" ]; then
        zenity --error --title="$TITLE" --text="$1" --no-wrap
    elif [ -n "$(command -v kdialog)" ]; then
        kdialog --error "$1" --title "$TITLE"
    elif [ -n "$(command -v notify-send)" ]; then
        notify-send "ERROR: $TITLE" "$1"
    elif [ -n "$(command -v xmessage)" ]; then
        xmessage -center "ERROR: $TITLE: $1"
    else
        printf "ERROR: %s\n%s\n" "$TITLE" "$1"
    fi
}

# 检查 python 是否安装, 获取 python 命令路径
if [ -n "$(command -v python)" ] || [ -n "$(command -v python3)" ]; then
    for tool in python python3; do
        test -n "$(command -v $tool)" && PYTHON_BIN_PATH="$(command -V $tool | awk '{print $3}')"
    done
    if [ -z "$PYTHON_BIN_PATH" ]; then
        message "no python or python3 command, please install python."
        exit 1
    fi
fi

# 检查需要的工具
if [ -z "$(command -v timedatectl)" ] || [ -z "$(command -v dconf)" ]; then
    TOOLS_MSG="Required tools are missing:\n"
    for tool in timedatectl dconf; do
        test -z "$(command -v $tool)" && TOOLS_MSG="$TOOLS_MSG $tool\n"
    done
    message "$TOOLS_MSG"
    exit 1
fi

# 获取当前文件目录
CURRENT_SCRIPT_DIR=$(
    cd "$(dirname "$0")" || exit 1
    pwd
)

# 后台执行 python 脚本
$PYTHON_BIN_PATH "${CURRENT_SCRIPT_DIR}/reset_navicat.py" &
