"""
Filename: reset_navicat.py
"""

import os
import subprocess
import datetime
from time import sleep
import json
from json import JSONDecodeError
import logging
from logging.handlers import RotatingFileHandler


def logger_config(log_path, console_print=True):
    """
    logger 日志的相关配置
    """
    log_dir = os.path.dirname(log_path)
    log_dir_exists = os.path.exists(log_dir)
    if not log_dir_exists:
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)
    # 日志最大文件大小 4M
    max_file_size = 1024 * 1024 * 4
    handler = RotatingFileHandler(
        log_path, maxBytes=max_file_size, backupCount=1, encoding="utf-8"
    )
    handler.setLevel(logging.DEBUG)
    # 设置日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s [%(levelname)s] - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if console_print:
        # console 控制台输出
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        logger.addHandler(console)
    return logger


def get_json_data(file_path):
    """
    从json文件中读取数据
    """
    dicts = {}
    with open(file_path, "r", encoding="utf8") as f:
        json_data = json.load(f)
        dicts = json_data
    return dicts


def write_json_data(file_path, data):
    """
    写入数据到json文件中
    """
    with open(file_path, "w", encoding="utf8") as r:
        json.dump(data, r, indent=4)


def check_network_connection_status(check_timeout_minutes=10):
    """
    检查网络连接
    """
    status = False
    network_check_count = check_timeout_minutes * 60 / 12
    while not status and network_check_count > 0:
        network_check_count -= 1
        try:
            network_check = subprocess.run(
                "ping www.bing.com -c 1",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                check=False,
            )
            if not network_check.returncode:
                status = True
                break
        except Exception:
            log.debug("网络未连接，2s 后将再次进行检查")
            sleep(2)
    if status:
        log.info("网络已连接")
    else:
        log.error("检查超时，网络未连接")
    return status


def check_ntp_service_status(check_timeout_minutes=10):
    """
    检查 NTP 时间同步服务
    """
    status = False
    ntp_service_check_count = check_timeout_minutes * 60 / 5
    while not status and ntp_service_check_count > 0:
        # 检查 NTP 时间同步服务是否启动
        ntp_service_check_count -= 1
        ntp_check = subprocess.run(
            'timedatectl status | grep NTP | cut -d ":" -f 2',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        ntp_service_msg = ntp_check.stdout
        if "inactive" in ntp_service_msg:
            log.info("NTP 时间同步服务未启动，即将重新开启 NTP 时间同步服务")
            log.debug("5s 后将再次检查 NTP 时间同步服务是否启动")
            subprocess.run(
                "timedatectl set-ntp false",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            sleep(1)
            subprocess.run(
                "timedatectl set-ntp true",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            sleep(4)
        else:
            status = True
            break
    if status:
        log.info("NTP 时间同步服务已启动")
    else:
        log.error("检查超时，NTP 时间同步服务未启动")
    return status


def check_time_sync_status(check_timeout_minutes=10):
    """
    检查时间同步状态
    """
    status = False
    time_sync_check_count = check_timeout_minutes * 60 / 5
    while not status and time_sync_check_count > 0:
        time_sync_check_count -= 1
        time_check = subprocess.run(
            'timedatectl status | grep synchronized | cut -d ":" -f 2',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        synced = time_check.stdout.strip()
        if "yes" in synced:
            status = True
            break
        log.debug("时间未从网络中同步，5s 后再次检查时间是否同步")
        sleep(5)
    if status:
        log.info("时间同步完成")
    else:
        log.error("检查超时，时间未同步")
    return status


def check_network_clock_sync():
    """
    检查网络时间是否同步

    检查步骤：网络连接 -> NTP 时间同步服务 -> 时间同步
    """
    time_sync_status = False
    network_connection_status = check_network_connection_status()
    if network_connection_status:
        ntp_service_status = check_ntp_service_status()
        if ntp_service_status:
            time_sync_status = check_time_sync_status()
    return time_sync_status


def need_to_reset_navicat():
    """
    判断是否需要重置 navicat 试用期
    """
    reset_json_file_exists = os.path.exists(RESET_JSON_INFO_FILE)
    if reset_json_file_exists:
        try:
            json_data = get_json_data(RESET_JSON_INFO_FILE)
            exists_filed = "reset_date" in json_data and "trial_period" in json_data
            if not exists_filed:
                log.info("脚本重置信息的 json 中缺失字段，即将重置 navicat 试用期")
                return True
            trial_period_str = json_data["trial_period"]
            trial_period = datetime.datetime.strptime(
                trial_period_str, DATE_FORMAT_PATTERN
            )
            # 距试用期剩余天数
            count_days = (trial_period - now_date).days
            if 0 < count_days <= 14:
                log.info(
                    "试用期至 %s, 下次重置将在 %d 天后进行",
                    trial_period_str,
                    count_days,
                )
                return False
            if count_days == 0:
                log.info(
                    "距试用期 %s 不到一天时间，即将重置 navicat 试用期",
                    trial_period_str,
                )
                return True
            log.info("距离试用过期过长或过短，即将重置 navicat 试用期")
            return True
        except JSONDecodeError as e:
            log.error("解析json文件错误：%s", e)
            log.info(
                "脚本重置信息的 json 文件无法解析，即将重置 navicat 试用期，重新生成json信息文件"
            )
            return True
    else:
        log.info(
            "脚本重置信息的 json 文件 [reset_date.json] 不存在, 即将重置 navicat 试用期"
        )
        return True


def update_navicat_reset_json_data(reseted):
    """
    生成更新脚本重置 navicat 试用期的信息数据
    """
    reset_date_str = now_date.strftime(DATE_FORMAT_PATTERN)
    trial_period_str = (now_date + datetime.timedelta(days=14)).strftime(
        DATE_FORMAT_PATTERN
    )
    if not reseted:
        json_data = get_json_data(RESET_JSON_INFO_FILE)
        reset_date_str = json_data["reset_date"]
        trial_period_str = json_data["trial_period"]
    reset_json = {
        # 检查日期
        "check_date": now_date.strftime(DATE_FORMAT_PATTERN),
        # 重置日期
        "reset_date": reset_date_str,
        # 试用期过期时间
        "trial_period": trial_period_str,
    }
    write_json_data(RESET_JSON_INFO_FILE, reset_json)


def reset_navicat():
    """
    重置 navicat 试用期
    """
    if need_to_reset_navicat():
        json_data = get_json_data(NAVICAT_PREFERENCES_JSON_PATH)
        # 移除相关键值
        for key in JSON_FIELD:
            json_data.pop(key, None)
        write_json_data(NAVICAT_PREFERENCES_JSON_PATH, json_data)
        update_navicat_reset_json_data(True)
        reset_need = subprocess.run(
            DCONF_RESET_CMD, shell=True, capture_output=True, text=True, check=False
        )
        reset_need_code = reset_need.returncode
        if reset_need_code:
            error_msg = reset_need.stderr
            log.error("dconf 重置 navicat 出现错误：%s", error_msg)
        else:
            log.info("dconf 重置 navicat 成功")
    else:
        update_navicat_reset_json_data(False)
        log.info("无需重置 navicat 试用期")


# 全局变量
DATE_FORMAT_PATTERN = "%Y-%m-%d %H:%M:%S"
USER_HOME_DIR = os.environ["HOME"]
BASE_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
NAVICAT_PREFERENCES_JSON_PATH = (
    USER_HOME_DIR + "/.config/navicat/Premium/preferences.json"
)
RESET_JSON_INFO_FILE = BASE_FILE_DIR + "/reset_date.json"
LOGGER_PATH = BASE_FILE_DIR + "/logs/reset_navicat.log"
DCONF_RESET_CMD = "dconf reset -f /com/premiumsoft/navicat-premium/"
now_date = datetime.datetime.now()
log = logger_config(LOGGER_PATH, console_print=False)
# 需要删除的 json 字段
JSON_FIELD = [
    # navicat 16 版本
    "B966DBD409B87EF577C9BBF3363E9614",
    # navicat 17 版本
    "014BF4EC24C114BEF46E1587042B3619"
]


if __name__ == "__main__":
    log.info("-----------------------------".center(50, "-"))
    log.info("检查重置 navicat 试用期".center(50))
    log.info("-----------------------------".center(50, "-"))
    # dconf 是清除 navicat 的主要命令
    result = subprocess.run(
        "command -v dconf > /dev/null 2>&1", shell=True, check=False
    )
    return_code = result.returncode
    if return_code:
        log.error("命令 dconf 不存在，请先安装 dconf")
    else:
        SYNC_STATUS = check_network_clock_sync()
        if SYNC_STATUS:
            now_date = datetime.datetime.now()
            log.info("时间已从网络中同步：%s", now_date.strftime(DATE_FORMAT_PATTERN))
        else:
            now_date = datetime.datetime.now()
            log.info(
                "时间同步失败，使用本机系统时间：%s，该时间直接影响到 navicat 的试用期",
                now_date.strftime(DATE_FORMAT_PATTERN),
            )
        reset_navicat()
