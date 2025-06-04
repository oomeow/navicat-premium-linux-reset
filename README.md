# navicat-premium-linux-reset

![License](https://img.shields.io/github/license/oomeow/navicat-premium-linux-reset)

## 免责声明

本脚本为免费使用，本脚本只供个人学习使用，使用需严格遵守开源许可协议。严禁用于商业用途，禁止进行任何盈利活动。对一切非法使用所产生的后果，概不负责！

---

该脚本通过删除 `preferences.json` 文件中相关字段，dconf 命令重置清除相关键值，来完成 navicat premium 的试用期重置

适用于 Linux 版本 navicat premium 的试用期

- 16.2.5 版本可用
- 17.2.2 版本可用
- 17.2.4 版本可用

**_navicat premium 其他版本尚未尝试_**

> 测试环境：
> 
> - Debian12 (Gnome)
> 
> - Arc Linux(KDE)
> 
> - Arch Linux(Gnome)
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
