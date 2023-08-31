#!/bin/bash

# python 命令路径
PYTHON_BIN_PATH=""
# USER_LOGIN=0
# DISPLAY_INFO=""
# DISPLAY_COUNT=60

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

# 检查 python 是否安装
if [ -n "$(command -v python)" ] || [ -n "$(command -v python3)" ]; then
  for tool in python python3; do
    test -n "$(command -v $tool)" && PYTHON_BIN_PATH="$(command -V $tool | awk '{print $3}')"
  done
  if [ -z $PYTHON_BIN_PATH ]; then
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
script_dir=$(
  cd $(dirname $0)
  pwd
)

# 等待用户登录
# while [ $USER_LOGIN -eq 0 ]; do
#   if [ -z "who | awk '{print $1}'" ]; then
#     echo "$(date "+%Y-%m-%d %H:%M:%S") - 用户未登录，等待用户登录" >>${script_dir}/shell_log.log
#     sleep 10s
#   else
#     USER_LOGIN=1
#   fi
# done

# dconf 需要 DISPLAY 值
# while [ -z $DISPLAY_INFO ] && [ $DISPLAY_COUNT -lt 0 ]; do
#   if [ -n "echo $DISPLAY | awk '{print $1}'" ]; then
#     DISPLAY_INFO="$(echo $DISPLAY | awk '{print $1}')"
#     echo "$(date "+%Y-%m-%d %H:%M:%S") - DISPLAY_INFO: $DISPLAY_INFO" >>${script_dir}/shell_log.log
#     sleep 2s
#   else
#     echo "$(date "+%Y-%m-%d %H:%M:%S") - 不存在 DISPLAY" >>${script_dir}/shell_log.log
#     DISPLAY_COUNT-=1
#     sleep 2s
#   fi
# done

# 后台执行 python 脚本
$PYTHON_BIN_PATH "${script_dir}/resetNavicat.py" &
