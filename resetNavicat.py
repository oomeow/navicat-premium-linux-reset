import json
import datetime
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from time import sleep


def logger_config(log_path, console_print=True):
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
    dicts = {}
    with open(file_path,'r',encoding='utf8') as f:
        json_data = json.load(f)
        dicts = json_data
    return dicts


def write_json_data(file_path, dict):
    with open(file_path,'w') as r:
        json.dump(dict,r)
        

def check_network_clock_sync(sync_timeout_minutes=60, ntp_toggle_count=10):
    global now_date
    # 网络连接检查
    network_check_sleep_second = 2
    network_check_count = sync_timeout_minutes * 60 / network_check_sleep_second
    network_check_cur_num = 0
    # 时间同步[需要互联网连接]
    time_sync_ntp_false_sleep_second = 1
    time_sync_ntp_true_sleep_second = 4
    time_sync_sum_sleep_second = time_sync_ntp_false_sleep_second + time_sync_ntp_true_sleep_second
    time_sync_count = sync_timeout_minutes * 60 / time_sync_sum_sleep_second
    # 时间同步状态
    time_sync_status = False
    while not time_sync_status:
        if network_check_cur_num < network_check_count:
            ping_result = subprocess.run('ping baidu.com -c 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if ping_result.returncode:
                network_check_cur_num += 1
                if network_check_cur_num < network_check_count:
                    log.debug('第%s次检查：网络未连接，2s 后将再次进行检查', network_check_cur_num)
                    sleep(network_check_sleep_second)
                else:
                    log.debug('第%s次检查：网络未连接', network_check_cur_num)
            else:
                log.info('网络已连接，检查时间，直到与网络时间同步了')
                sync_time_result = subprocess.run('timedatectl status | grep synchronized | cut -d ":" -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                synced = sync_time_result.stdout.strip()
                if 'yes' in synced:
                    now_date = datetime.datetime.now()
                    log.info('检查到时间已同步，当前时间：%s', now_date.strftime(format_pattern))
                    time_sync_status = True
                else:
                    time_sync_count -= 1
                    if time_sync_count == 0:
                        log.error('%s分钟内，时间未能进行同步', sync_timeout_minutes)
                        break
                    log.debug('5s 后将再次检查时间是否同步')
                    if ntp_toggle_count > 0:
                        # 检查 ntp 服务是否激活了
                        ntp_service_result = subprocess.run('timedatectl status | grep NTP | cut -d ":" -f 2', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        ntp_service_msg = ntp_service_result.stdout
                        if "inactive" in ntp_service_msg:
                            ntp_toggle_count -= 1
                            # sudo 交互式输入命令设置 ntp
                            # p1 = subprocess.Popen('sudo -S timedatectl set-ntp false', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            # outs, errs = p1.communicate(bytes(auth_password, 'utf-8'), timeout=10)
                            # p1.wait()
                            # log.debug(str(outs, 'utf-8'))
                            # log.debug(str(errs, 'utf-8'))
                            subprocess.run('timedatectl set-ntp false', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            sleep(time_sync_ntp_false_sleep_second)
                            # sudo 交互式输入命令设置 ntp
                            # p2 = subprocess.Popen('sudo -S timedatectl set-ntp true', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            # outs, errs = p2.communicate(bytes(auth_password, 'utf-8'), timeout=10)
                            # p2.wait()
                            # log.debug(str(outs, 'utf-8'))
                            # log.debug(str(errs, 'utf-8'))
                            subprocess.run('timedatectl set-ntp true', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            sleep(time_sync_ntp_true_sleep_second)
                        else:
                            sleep(time_sync_sum_sleep_second)
                    else:
                        sleep(time_sync_sum_sleep_second)
        else:
            now_date = datetime.datetime.now()
            log.warning('%d 次网络检查均未发现网络连接，将使用本机系统时间 %s，该时间直接影响到 navicat 的试用期', network_check_count, now_date.strftime(format_pattern))
            break
    return time_sync_status


def need_to_reset_navicat():
    reset_json_file_exists = os.path.exists(reset_json_info_file)
    if reset_json_file_exists:
        json_data = get_json_data(reset_json_info_file)
        exists_filed = 'trial_period' in json_data
        if not exists_filed:
            log.info('试用期限字段不存在，需要重置 navicat 试用期限')
            return True
        next_reset_date_str = json_data['trial_period']
        next_reset_date = datetime.datetime.strptime(next_reset_date_str, format_pattern)
        count_days = (next_reset_date - now_date).days
        if count_days > 0 and count_days <= 14:
            log.info('试用期 %s, 下次重置将在 %d 天后进行', next_reset_date_str, count_days)
            return False
        elif count_days == 0:
            log.info('距试用期 %s 不到一天时间，即将重置 navicat 试用期限', next_reset_date_str)
            return True
        else:
            log.info('距离试用过期过长或过短，即将重置 navicat 试用期限')
            return True
    else:
        log.info('reset_navicat.json 文件不存在, 即将重置 navicat 试用期限')
        return True


def write_navicat_reset_date(reseted=True):
    reset_date_str = now_date.strftime(format_pattern)
    trial_period_str = (now_date + datetime.timedelta(days=14)).strftime(format_pattern)
    reset_dict = {
        'check_date': now_date.strftime(format_pattern),
    }
    reset_json_file_exists = os.path.exists(reset_json_info_file)
    if reset_json_file_exists:
        json_data = get_json_data(reset_json_info_file)
        if not 'reset_date' in json_data or reseted:
            reset_dict['reset_date'] = reset_date_str
            reset_dict['trial_period'] = trial_period_str
        else:
            reset_date_str = json_data['reset_date']
            trial_period_str = json_data['trial_period']
            reset_dict['reset_date'] = reset_date_str
            reset_dict['trial_period'] = trial_period_str
    if reseted:
        reset_dict['reset_date'] = reset_date_str
        reset_dict['trial_period'] = trial_period_str
    write_json_data(reset_json_info_file, reset_dict)
            

def reset_navicat():
    if need_to_reset_navicat():
        json_data = get_json_data(navicat_preferences_json_path)
        # 移除 B966DBD409B87EF577C9BBF3363E9614 键值
        json_data.pop('B966DBD409B87EF577C9BBF3363E9614', None)
        write_json_data(navicat_preferences_json_path, json_data)
        write_navicat_reset_date()
        result = subprocess.run(dconf_reset_cmd, shell=True, capture_output=True, text=True)
        error_msg = result.stderr
        return_code = result.returncode
        if return_code:
            log.error('重置 dconf 出现错误：%s', error_msg)
        else:
            log.info('重置 dconf 执行成功')
    else:
        write_navicat_reset_date(reseted=False)
        log.info('无需重置 navicat 试用期限')


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
    
    result = subprocess.run('command -v dconf > /dev/null 2>&1', shell=True)
    return_code = result.returncode
    if return_code:
        log.error('命令 dconf 不存在，请先安装 dconf')
    else:
        check_network_clock_sync()
        reset_navicat()