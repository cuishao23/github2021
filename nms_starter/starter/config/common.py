"""
nms_starter settings
"""
import os

from utils.common import get_conf

############## 路径配置 ##############
# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), 'etc/nms_starter.ini')
SCRIPT_DIR = os.path.join(BASE_DIR, 'script')
TERMINAL_TYPE_XLSX = os.path.join(BASE_DIR, 'data', 'terminal_type.xlsx')


############## 日志配置 ##############
LOGGING = {
    'loggername': 'nms_starter',
    'format': '[%(levelname)s] %(asctime)s %(pathname)s %(lineno)s: %(message)s',
    # 等级标准
    # 日常开发调试: debug
    # 关键节点: info
    # 部分合理存在错误: warning
    # 异常,非合理性错误: error
    'level': 'DEBUG',
    'log_path': '/opt/log/nms_starter',
}


############## 资源限制 ##############
# 消息队列最大长度
MAX_MSG_QUEUE_LEN = 100000
# 线程消息队列最大接收阻塞时间,等待此时间还未收到消息触发Empty异常,单位 秒
MAX_QUEUE_WAITING_TIME = 3600 * 24
REDIS_LIMIIT = {
    # redis最大连接数
    'max_connections': 10,
    # 链接健康检查
    'health_check_interval': 30,
}

# 服务器默认资源限制
SERVER_RESOURCE_LIMIT = {
    'cpu': 80,
    'memory': 80,
    'disk': 80,
    'diskage': 80,
    'port': 60,
    'diskwritespeed': 2,
    'rateofflow': 500
}


############## 线程配置 ##############

PHYSICAL_MSG_THREAD_NAME = 'physical_msg_thread'
LOGICAL_MSG_THREAD_NAME = 'logical_msg_thread'
TERMINAL_MSG_THREAD_NAME = 'terminal_msg_thread'
TERMINAL_26_MSG_THREAD_NAME = 'terminal_26_msg_thread'
TERMINAL_48_MSG_THREAD_NAME = 'terminal_48_msg_thread'
WEBSERVER_MSG_THREAD_NAME = 'webserver_msg_thread'
BMC_MSG_THREAD_NAME = 'bmc_msg_thread'
LUBAN_MSG_THREAD_NAME = 'luban_msg_thread'
REDIS_TASK_THREAD_NAME = 'redis_task_thread'
LUBAN_MQ_THREAD_NAME = 'luban_mq_thread'
CONFMGR_MQ_THREAD_NAME = 'confmgr_mq_thread'
TIMING_INSPECTION_THREAD_NAME = 'timing_inspection_thread'


# 导入标志, 如果数据更新导致升级需要更重新导入, 更新此标志版本号
IMPORT_FLAG = get_conf('nms', 'version', CONFIG_PATH)

############## 连接配置 ##############
# rmq
AMQP_URL = 'amqp://{user}:{password}@{host}:{port}/'.format(
    user="dev",
    password="dev",
    host=get_conf('rabbitmq', 'host', CONFIG_PATH),
    port=int(get_conf('rabbitmq', 'port', CONFIG_PATH))
)
COLLECTOR_CONSUMER = {
    "exchange": "nms.collector.ex",
    "exchange_type": 'topic',
    "queue": "collector.nms.q",
    "routing_key": "collector.nms.k"
}
MEETING_CONSUMER = {
    "exchange": "nms.collector.ex",
    "exchange_type": 'topic',
    "queue": "collector.nms.q",
    "routing_key": "collector.nms.k"
}
COLLECTOR_HEARTBEAT_CONSUMER = {
    "exchange": "nms.collector.ex",
    "exchange_type": 'topic',
    "queue": "collector.heartbeat.q",
    "routing_key": "collector.heartbeat.k"
}
INSPECT_CONSUMER = {
    "exchange": "nms.webserver.ex",
    "exchange_type": 'topic',
    "queue": "nms.inspection.q",
    "routing_key": "nms.inspection.k"
}
BMC_CONSUMER = {
    "exchange": "movision.nms.ex",
    "exchange_type": 'topic',
    "queue": "nms.datasync.q",
    "routing_key": "nms.datasync.k"
}

REDIS = {
    "host": get_conf('redis', 'host', CONFIG_PATH),
    "port": int(get_conf('redis', 'port', CONFIG_PATH)),
    # "db": 2,
    "password": get_conf('redis', 'password', CONFIG_PATH)
}

DB_ENGINE = 'mysql+pymysql' if get_conf('nms', 'db_engine',
                                        CONFIG_PATH) == 'mysql' else 'postgresql'
MYSQL = '{engine}://{user}:{password}@{host}:{port}/{db}'.format(
    engine=DB_ENGINE,
    host=get_conf('mysql', 'host', CONFIG_PATH),
    port=get_conf('mysql', 'port', CONFIG_PATH),
    db="nms_db",
    user=get_conf('mysql', 'user', CONFIG_PATH),
    password=get_conf('mysql', 'password', CONFIG_PATH)
)
BMC_MYSQL = '{engine}://{user}:{password}@{host}:{port}/{db}'.format(
    engine=DB_ENGINE,
    host=get_conf('mysql', 'host', CONFIG_PATH),
    port=int(get_conf('mysql', 'port', CONFIG_PATH)),
    db="movision",
    user=get_conf('mysql', 'user', CONFIG_PATH),
    password=get_conf('mysql', 'password', CONFIG_PATH)
)
LUBAN_MYSQL = '{engine}://{user}:{password}@{host}:{port}/{db}'.format(
    engine=DB_ENGINE,
    host='[{}]'.format(get_conf('luban_mysql', 'host', CONFIG_PATH)) if ':' in get_conf(
        'luban_mysql', 'host', CONFIG_PATH) else get_conf('luban_mysql', 'host', CONFIG_PATH),
    port=get_conf('luban_mysql', 'port', CONFIG_PATH),
    db="luban",
    user=get_conf('luban_mysql', 'user', CONFIG_PATH),
    password=get_conf('luban_mysql', 'password', CONFIG_PATH)
)

# mail
MAIL = get_conf('nms', 'mail', CONFIG_PATH)

# 短信
SERVICE_IP = get_conf('nms', 'service_core_ip', CONFIG_PATH)
SERVICE_PORT = get_conf('nms', 'service_core_port', CONFIG_PATH)

# API CORE
API_CORE_IP = get_conf('nms', 'api_core_ip', CONFIG_PATH)
API_CORE_PORT = get_conf('nms', 'api_core_port', CONFIG_PATH)

# graphite
GRAPHITE_IP = '[{}]'.format(get_conf('nms', 'graphite_ip', CONFIG_PATH)) if ':' in get_conf(
    'nms', 'graphite_ip', CONFIG_PATH) else get_conf('nms', 'graphite_ip', CONFIG_PATH)
GRAPHITE_PORT = get_conf('nms', 'graphite_port', CONFIG_PATH)

# nms server
NMS_SERVER_IP = get_conf('nms', 'nms_server_ip', CONFIG_PATH)
NMS_SERVER_PORT = get_conf('nms', 'nms_server_port', CONFIG_PATH)

# 品牌
BRAND = get_conf('nms', 'brand', CONFIG_PATH)

# 会议评分
SCORE = {
    'lossrate': {
        'step':  int(get_conf('score', 'lossrate_step', CONFIG_PATH)),
        'score':  float(get_conf('score', 'lossrate_score', CONFIG_PATH))
    },
    'blunt': {
        'step':  int(get_conf('score', 'blunt_step', CONFIG_PATH)),
        'score':  float(get_conf('score', 'blunt_score', CONFIG_PATH))
    },
    'offline': {
        'step':  int(get_conf('score', 'offline_step', CONFIG_PATH)),
        'score':  float(get_conf('score', 'offline_score', CONFIG_PATH))
    },
}
