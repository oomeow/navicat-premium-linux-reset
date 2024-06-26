# navicat-premium-linux-reset

该脚本通过删除 `preferences.json` 文件中 `B966DBD409B87EF577C9BBF3363E9614` 字段，dconf 命令重置清除相关键值，来完成 navicat premium 的试用期重置

适用于 Linux 版本 navicat premium 的试用期

- 16.2.5 版本可用

**_navicat premium 其他版本尚未尝试_**

> 测试系统：Debian12
>
> 测试桌面环境：Gnome

## 用法

执行 shell 脚本，或使用 python 命令执行 python 脚本

```shell
# 方式一：执行 shell 脚本
./reset_navicat.sh

# 方式二：python 命令执行 python 脚本
python reset_navicat.py
```

## 设置用户开机登录后启动脚本

### install 脚本

```shell
# 开启
./install.sh

# 关闭
./install.sh -u
```

### 手动

```shell
# 编辑用户目录下的 .profile 文件
vim ~/.profile

# 添加脚本命令
# 例如：bash "$HOME/navicat-premium-linux-reset/reset_navicat.sh"
bash shell脚本路径

# KDE下，如果上面脚本命令不起作用，可以使用 autostart
# 具体方法：
#   1.复制 `template.desktop` 文件（新的文件名随意, 例如： reset_navicat.sh.desktop）
#   2.修改复制的新文件 (reset_navicat.sh.desktop)，将 script_path 替换为 reset_navicat.sh 脚本绝对的路径
#   3.将复制的新文件 (reset_navicat.sh.desktop) 移动到 autostart 目录（一般在 `$HOME/.config/autostart/` ）
```

## 重置 navicat 的思路

### 1、删除 json 文件中指定字段

<img src="./images/json.png" alt="删除指定字段" style="border: 2px solid rgba(0,0,0,.2); box-shadow: 10px 10px 10px rgba(0,0,0,.4);"/>

### 2、dconf 中需要重置的 navicat 相关的键值

<img src="./images/dconf.png" alt="dconf 重置 navicat 相关的键值" style="border: 2px solid rgba(0,0,0,.2); box-shadow: 10px 10px 10px rgba(0,0,0,.4);"/>
