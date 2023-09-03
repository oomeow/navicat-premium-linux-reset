import os
import subprocess
import datetime
from time import sleep
import json
from json import JSONDecodeError
import logging
from logging.handlers import RotatingFileHandler


def logger_config(log_path, console_print=True):
    '''
    logger 日志的相关配置
    '''
    log_dir = os.path.dirname(log_path)
    log_dir_exists = os.path.exists(log_dir)
    if not log_dir_exists:
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(level=logging.DEBUG)
    # 日志最大文件大小 4M
    max_file_size = 1024 * 1024 * 4
    handler = RotatingFileHandler(log_path, maxBytes=max_file_size, backupCount=1, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(filename)s [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if console_print:
        # console 控制台输出
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        logger.addHandler(console)
    return logger


def get_json_data(file_path):
    '''
    从json文件中读取数据
    '''
    dicts = {}
    with open(file_path,'r',encoding='utf8') as f:
        json_data = json.load(f)
        dicts = json_data
    return dicts


def write_json_data(file_path, dict):
    '''
    写入数据到json文件中
    '''
    with open(file_path,'w') as r:
        json.dump(dict,r)


def check_network_connection_status(check_timeout_minutes=60, check_time_interval_second=2):
    '''
    检查网络连接
    '''
    status = False
    network_check_count = check_timeout_minutes * 60 / check_time_interval_second
    while not status and network_check_count > 0:
        network_check_count -= 1
        result = subprocess.run('ping baidu.com -c 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if not result.returncode:
            status = True
            break
        else:
            log.debug('网络未连接，%ss 后将再次进行检查', check_time_interval_second)
            sleep(check_time_interval_second)
    if status:
        log.info('网络已连接')
    else:
        log.error('检查超时，网络未连接')
    return status


def check_ntp_service_status(check_timeout_minutes=10):
    '''
    检查 NTP 时间同步服务
    '''
    status = False
    ntp_service_check_count = check_timeout_minutes * 60 / 5
    while not status and ntp_service_check_count > 0:
        # 检查 NTP 时间同步服务是否启动
        ntp_service_check_count -= 1
        result = subprocess.run('timedatectl status | grep NTP | cut -d ":" -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ntp_service_msg = result.stdout
        if "inactive" in ntp_service_msg:
            log.info('NTP 时间同步服务未启动，即将重新开启 NTP 时间同步服务')
            log.debug('5s 后将再次检查 NTP 时间同步服务是否启动')
            # sudo 交互式输入命令设置 ntp
            # p1 = subprocess.Popen('sudo -S timedatectl set-ntp false', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # outs, errs = p1.communicate(bytes(auth_password, 'utf-8'), timeout=10)
            # p1.wait()
            # log.debug(str(outs, 'utf-8'))
            # log.debug(str(errs, 'utf-8'))
            subprocess.run('timedatectl set-ntp false', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sleep(1)
            # sudo 交互式输入命令设置 ntp
            # p2 = subprocess.Popen('sudo -S timedatectl set-ntp true', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # outs, errs = p2.communicate(bytes(auth_password, 'utf-8'), timeout=10)
            # p2.wait()
            # log.debug(str(outs, 'utf-8'))
            # log.debug(str(errs, 'utf-8'))
            subprocess.run('timedatectl set-ntp true', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            sleep(4)
        else:
            status = True
            break
    if status:
        log.info('NTP 时间同步服务已启动')
    else:
        log.error('检查超时，NTP 时间同步服务未启动')
    return status


def check_time_sync_status(check_timeout_minutes=60, check_time_interval_second=5):
    '''
    检查时间同步状态
    '''
    status = False
    time_sync_check_count = check_timeout_minutes * 60 / 5
    while not status and time_sync_check_count > 0:
        time_sync_check_count -= 1
        result = subprocess.run('timedatectl status | grep synchronized | cut -d ":" -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        synced = result.stdout.strip()
        if 'yes' in synced:
            status = True
            break
        log.debug('时间未从网络中同步，%ss 后再次检查时间是否同步', check_time_interval_second)
        sleep(check_time_interval_second)
    if status:
        log.info('时间同步完成')
    else:
        log.error('检查超时，时间未同步')
    return status


def check_network_clock_sync():
    '''
    检查网络时间是否同步
    
    检查步骤：网络连接 -> NTP 时间同步服务 -> 时间同步
    '''
    time_sync_status = False
    network_connection_status = check_network_connection_status()
    if network_connection_status:
        ntp_service_status = check_ntp_service_status()
        if ntp_service_status:
            time_sync_status = check_time_sync_status()
    return time_sync_status


def need_to_reset_navicat():
    '''
    判断是否需要重置 navicat 试用期
    '''
    reset_json_file_exists = os.path.exists(reset_json_info_file)
    if reset_json_file_exists:
        try:
            json_data = get_json_data(reset_json_info_file)
            exists_filed = 'reset_date' in json_data and 'trial_period' in json_data
            if not exists_filed:
                log.info('脚本重置信息的 json 中缺失字段，需要重置 navicat 试用期')
                return True
            next_reset_date_str = json_data['trial_period']
            next_reset_date = datetime.datetime.strptime(next_reset_date_str, format_pattern)
            count_days = (next_reset_date - now_date).days
            if count_days > 0 and count_days <= 14:
                log.info('试用期至 %s, 下次重置将在 %d 天后进行', next_reset_date_str, count_days)
                return False
            elif count_days == 0:
                log.info('距试用期 %s 不到一天时间，即将重置 navicat 试用期', next_reset_date_str)
                return True
            else:
                log.info('距离试用过期过长或过短，即将重置 navicat 试用期')
                return True
        except JSONDecodeError as e:
            log.error('解析json文件错误：%s', e)
            log.info('脚本重置信息的 json 文件无法解析，即将重置 navicat 试用期，重新生成json信息文件')
            return True
    else:
        log.info('脚本重置信息的 json 文件 [reset_navicat.json] 不存在, 即将重置 navicat 试用期')
        return True


def update_navicat_reset_json_data(reseted):
    '''
    生成更新脚本重置 navicat 试用期的信息数据
    '''
    reset_date_str = now_date.strftime(format_pattern)
    trial_period_str = (now_date + datetime.timedelta(days=14)).strftime(format_pattern)
    if not reseted:
        json_data = get_json_data(reset_json_info_file)
        reset_date_str = json_data['reset_date']
        trial_period_str = json_data['trial_period']
    reset_json = {
        'check_date': now_date.strftime(format_pattern),
        'reset_date': reset_date_str,
        'trial_period': trial_period_str
    }
    write_json_data(reset_json_info_file, reset_json)
            

def reset_navicat():
    '''
    重置 navicat 试用期
    '''
    if need_to_reset_navicat():
        json_data = get_json_data(navicat_preferences_json_path)
        # 移除 B966DBD409B87EF577C9BBF3363E9614 键值
        json_data.pop('B966DBD409B87EF577C9BBF3363E9614', None)
        write_json_data(navicat_preferences_json_path, json_data)
        update_navicat_reset_json_data(True)
        result = subprocess.run(dconf_reset_cmd, shell=True, capture_output=True, text=True)
        return_code = result.returncode
        if return_code:
            error_msg = result.stderr
            log.error('dconf 重置 navicat 出现错误：%s', error_msg)
        else:
            log.info('dconf 重置 navicat 成功')
    else:
        update_navicat_reset_json_data(False)
        log.info('无需重置 navicat 试用期')


if __name__ == '__main__':
    # 常量
    format_pattern = '%Y-%m-%d %H:%M:%S'
    user_home_dir = os.environ['HOME']
    # sudo 需要输入的命令
    # auth_password = '123456'
    base_file_dir = os.path.dirname(os.path.abspath(__file__))
    navicat_preferences_json_path = user_home_dir + '/.config/navicat/Premium/preferences.json'
    reset_json_info_file = base_file_dir + '/reset_navicat.json'
    logger_path = base_file_dir + '/logs/reset_navicat.log'
    dconf_reset_cmd = 'dconf reset -f /com/premiumsoft/navicat-premium/'
    
    # 变量
    now_date = datetime.datetime.now()
    log = logger_config(logger_path, console_print=False)
    
    log.info('-----------------------------'.center(50, '-'))
    log.info('检查重置 navicat 试用期'.center(50))
    log.info('-----------------------------'.center(50, '-'))
    # dconf 是清除 navicat 的主要命令
    result = subprocess.run('command -v dconf > /dev/null 2>&1', shell=True)
    return_code = result.returncode
    if return_code:
        log.error('命令 dconf 不存在，请先安装 dconf')
    else:
        sync_status = check_network_clock_sync()
        if sync_status:
            now_date = datetime.datetime.now()
            log.info('时间已从网络中同步：%s', now_date.strftime(format_pattern))
        else:
            now_date = datetime.datetime.now()
            log.info('时间同步失败，使用本机系统时间：%s，该时间直接影响到 navicat 的试用期', now_date.strftime(format_pattern))
        reset_navicat()