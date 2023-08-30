# navicat-premium-reset
该脚本通过删除json文件特定字段，dconf重置清除相关键值来完成 navicat premium 的试用期重置

适用于 Linux 版本 navicat premium 的试用期

- 16.2.5 版本可用

> navicat premium 其他版本尚未尝试



#### Linux 开机执行脚本

可通过将 shell 脚本加入到 crontab 中来完成

```shell
# 编辑此用户下的 crontab
crontab -e

# 添加这一行命令
@reboot shell脚本的路径
```

