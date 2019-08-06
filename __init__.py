import os
import sys

__dir__ = os.path.abspath(os.path.dirname(__file__))
__root__ = os.path.dirname(__dir__)
if __dir__ not in sys.path:
    sys.path.append(__dir__)
if __root__ not in sys.path:
    sys.path.append(__root__)

import datetime
import requests
from pymongo import MongoClient
from ServerCrashWarningToWeiXin.setting import *

client = MongoClient(HOST, PORT)
collection = client.flow_logs.workers


def push_weixin_msg(key, title, content=None):
    r"""Sends a warning message

    :param key: Server酱扫描二维码生成SCKEY.
    :param title: 消息的标题头.
    :param content：消息的内容.
    :rtype: True 发送成功, False 发送失败.
    """
    url = f'https://sc.ftqq.com/{key}.send'
    params = {
        "text": str(datetime.datetime.now()) + title,
        "desp": str(datetime.datetime.now()) + content,
    }
    resp = requests.get(url, params=params)
    j = resp.json()
    if 'errmsg' in j and j['errmsg'] == 'success':
        return True
    else:
        return False


def get_servers_diff_utctime(hostname):
    server_info = collection.find_one({'hostname': hostname})
    current_datetime = datetime.datetime.utcnow()
    date_update = server_info['date_update']
    diff_time = current_datetime.timestamp() - date_update.timestamp()
    if "group" in server_info and server_info["group"] == "test":
        diff_time = 0
    return diff_time


def get_total_chromedrivers():
    CCursor = collection.aggregate([{"$group": {"_id": None, "num_target": {"$sum": "$length_browsers_now"}}}])
    for data in CCursor:
        return data['num_target']


def push_crash_msg():
    servers_status = {}
    for hostname in SERVERS_HOSTS:
        servers_status[hostname] = get_servers_diff_utctime(hostname)
    is_auto_reboot = 0  # 是否发送警报消息，0为不发送，大于0发送
    crash_servers_reboot = []
    for key, value in servers_status.items():
        if value > CRASH_TIME * 60:  # 查找已崩溃的服务器
            crash_servers_reboot.append(key)
        if value > CRASH_TIME * 60 and value < CRASH_TIME * 60 * RESTART_TIMES:
            is_auto_reboot += 1
    if is_auto_reboot == len(SERVERS_HOSTS):
        os.system(f"/home/c/test_fab/expect_single.sh 'localhost' \"su root -c 'shutdown -r now'\"")
        for sc_key in SCKEY_LIST_ADVANCED:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，主服务器崩溃了，正在尝试自动重启，有空就去看看吧')
    if is_auto_reboot > 0:
        str_hostname = ""
        for hostname in crash_servers_reboot:
            os.system(f"/home/c/test_fab/expect_single.sh {hostname} \"su root -c 'init 6'\"")
            str_hostname += hostname + "，"
        for sc_key in SCKEY_LIST_ADVANCED:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，服务器{str_hostname}崩溃了，正在尝试自动重启，有空就去看看吧')

    is_push_msg = 0  # 是否发送警报消息，0为不发送，大于0发送
    crash_servers = []
    for key, value in servers_status.items():
        if value > CRASH_TIME * 6 * 60:  # 查找已崩溃的服务器
            crash_servers.append(key)
        if value > CRASH_TIME * 6 * 60 and value < CRASH_TIME * 6 * 60 * RESTART_TIMES:
            is_push_msg += 1
    if is_push_msg == len(SERVERS_HOSTS):
        os.system(f"/home/c/test_fab/expect_single.sh 'localhost' \"su root -c 'shutdown -r now'\"")
        for sc_key in SCKEY_LIST_ADVANCED:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，服务器{str_hostname}崩溃了，正在尝试自动重启，有空就去看看吧')
    if is_push_msg > 0:
        str_hostname = ""
        for hostname in crash_servers:
            os.system(f"/home/c/test_fab/expect_single.sh {hostname} \"su root -c 'shutdown -r now'\"")
            str_hostname += hostname + "，"
        for sc_key in SCKEY_LIST_ADVANCED:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，服务器{str_hostname}崩溃了，正在尝试自动重启，有空就去看看吧')
        for sc_key in SCKEY_LIST:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，服务器{str_hostname}崩溃了，自动重启失败，赶紧想想办法吧')
    if get_total_chromedrivers() < CHROMEDRIVERS_THRESHOLD:
        os.chdir("/home/c")
        os.system("docker-compose restart")
        os.system(f"su c -c '/home/c/test_fab/expect_ssh.sh \"pgrep -f v2.py|xargs kill -9\"'")
        os.system(f"su c -c '/home/c/test_fab/expect_ssh.sh \"pgrep -f chrome|xargs kill -9\"'")
        for sc_key in SCKEY_LIST_ADVANCED:
            push_weixin_msg(sc_key, MSG_TITLE, f'主人，服务器{str_hostname}崩溃了，正在尝试自动重启，有空就去看看吧')


if __name__ == '__main__':
    push_crash_msg()
