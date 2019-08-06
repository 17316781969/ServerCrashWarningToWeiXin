# mongodb 参数
HOST = "192.168.2.100"
PORT = 27017

# 监控主机列表
SERVERS_HOSTS = ['apple-001', 'apple-002', 'apple-003', 'apple-004', 'apple-005']

# Server酱二维码生成SCKEY列表(告警发送对象)
SCKEY_LIST = ['SCU35834Tc10cc37bc073e0e8fbf4b9775ad70d3e5bed120739a0a',
              'SCU35833T5d98d43b5e735deb3621cc20495226075bed121682c81']
SCKEY_LIST_ADVANCED = ['SCU35833T5d98d43b5e735deb3621cc20495226075bed121682c81', ]
# 告警标题
MSG_TITLE = "服务器崩溃"

# 阀值参数等
CRASH_TIME = 5  # 心跳停止时长（分）
RESTART_TIMES = 3  # 尝试重启次数
CHROMEDRIVERS_THRESHOLD = 3  # chromedriver总数低于此值时，告警
