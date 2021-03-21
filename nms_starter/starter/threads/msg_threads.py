'''
消息处理线程
'''
import logging
from retry import retry
from threads.base import MsgProcessThread
from config.common import LOGGING
from utils.lock import synchronized

logger = logging.getLogger(LOGGING['loggername'])


class BmcMsgThread(MsgProcessThread):
    '''
    接收bmc_mq_thread发送过来的消息,根据消息operation调用不同的函数进行处理
    '''

    def __init__(self, name):
        super().__init__(name=name)

    @retry(tries=3, delay=2, backoff=2, logger=logger)
    @retry(tries=3)
    def dispatch(self, msg):
        from core import bmc_msg_handler
        logger.info("[%s] msg: %s" % (self._name, msg))
        try:
            eventid = msg['operation']
            func = eval('bmc_msg_handler.%s' % eventid)
            if not callable(func):
                raise Exception('not a function')
        except Exception:
            logger.error(
                '[%s]:cannot find message handler' % self._name)
        else:
            func(msg)


class BusinessMsgThread(MsgProcessThread):
    '''
    接收collector_mq_thread发送过来的消息,根据消息类型调用不同的函数进行处理
    '''

    def __init__(self, name, handler):
        self._handler = handler
        super().__init__(name=name)

    @retry(tries=3, delay=2, backoff=2, logger=logger)
    @retry(tries=3)
    def dispatch(self, msg):
        from core import logical_msg_handler, physical_msg_handler, terminal_msg_handler, terminal_26_msg_handler, terminal_48_msg_handler, meeting_msg_handler
        logger.info("[%s] msg: %s" % (self._name, msg))
        try:
            eventid = msg['eventid'].lower()
            func = eval('%s.%s' % (self._handler, eventid))
            if not callable(func):
                raise Exception('not a function')
        except Exception:
            logger.error(
                '[%s]:cannot find message handler' % self._name)
        else:
            func(msg)


class MySQLWriteThread(MsgProcessThread):
    '''
    MySQL写入线程
    '''

    def __init__(self, name):
        super().__init__(name)

    @retry(tries=3, delay=2, backoff=2, logger=logger)
    @retry(tries=3)
    def dispatch(self, msg):
        from dao import nms_mysql
        from dao.mysql import nms_session_scope
        logger.info("[%s] msg: %s" % (self._name, msg))
        if callable(msg[0]):
            with nms_session_scope() as session:
                msg[0](session, msg[1])
        else:
            logger.error('[%s]: data error!' % self._name)


class GraphiteStatisticTask(MsgProcessThread):
    '''
    Graphite统计线程
    '''

    def __init__(self, name):
        self.socket = None
        super().__init__(name)

    def init_connect(self):
        import socket
        from config.common import GRAPHITE_IP, GRAPHITE_PORT
        logger.info('[%s] init connect %s:%s' % (self._name, GRAPHITE_IP, GRAPHITE_PORT))
        if ':' in GRAPHITE_IP:
            # ipv6
            self.socket = socket.socket(socket.AF_INET6)
            self.socket = socket.connect((
                GRAPHITE_IP, int(GRAPHITE_PORT), 0, 0))
        else:
            # ipv4
            self.socket = socket.socket()
            self.socket.connect((GRAPHITE_IP, int(GRAPHITE_PORT)))

    @retry(delay=1, backoff=2, max_delay=60)
    def dispatch(self, msg):
        if self.socket is None:
            self.init_connect()
        try:
            self.socket.sendall(msg.encode('utf-8'))
        except Exception as e:
            logger.error('[%s] %s' % (self._name, e))
            if self.socket is not None:
                self.socket.close()
            self.init_connect()
            raise Exception


mysql_write_thread = MySQLWriteThread('mysql_write_thread')
graphite_statistic_thread = GraphiteStatisticTask('graphite_statistic_thread')
