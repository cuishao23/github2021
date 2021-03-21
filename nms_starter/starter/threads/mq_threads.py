'''
mq消息监听线程
'''
import logging
import pika
from threading import Timer
from datetime import datetime
from retry import retry
from threads.base import RMQConsumerThread, MsgProcessThread
from threads.msg_threads import BmcMsgThread, BusinessMsgThread
from config.common import LOGGING, AMQP_URL, COLLECTOR_CONSUMER
from config.types import server_type_judgment

logger = logging.getLogger(LOGGING['loggername'])


class BmcMQThread(RMQConsumerThread):
    '''
    本线程监听bmc发送的消息: 用户/域/机房/老终端/license
    并将消息会发送到bmc_msg_thread线程进行处理
    '''

    def __init__(self, name, mq_arg):
        self.bmc_msg_thread = BmcMsgThread('bmc_msg_thread')
        self.bmc_msg_thread.start()
        super().__init__(name, mq_arg)

    def dispatch(self, msg):
        '''
        把消息分发到对应的处理函数
        :param msg:
        :return:
        '''
        if 'operation' not in msg:
            logger.warning('[%s]: msg format wrong' % self._name)
        else:
            self.bmc_msg_thread.push(msg)


class HeartbeatMQThread(RMQConsumerThread):
    '''
    collector心跳处理线程, 每个collector上线后绑定一个定时器, 超时时间为30秒,
    超时后下线所有连接该collector的设备并删除该collector
    '''

    def __init__(self, name, mq_arg):
        self._collector = {}
        self._thread = {}
        super().__init__(name, mq_arg)

    def dispatch(self, msg):
        '''
        把消息分发到对应的处理函数
        :param msg:
        :return:
        '''
        try:
            collectorid = msg['collectorid']
            devid = msg['guard_guid']
        except Exception:
            logger.error('[%s] msg format wrong' % self._name)
            return

        # 回复collector心跳ack
        self._ack_collector(collectorid, devid)

        # 心跳超时任务更新
        if collectorid in self._collector:
            self._update_timer(collectorid)
        else:
            logging.info('[%s] collector online %s' %
                         (self._name, collectorid))
            self._add_timer(collectorid)
            self._collector_online(collectorid, devid)

    def _ack_collector(self, collectorid, devid):
        '''
        回复collector EV_COLLECTOR_HEARTBEAT_ACK
        :param collectorid:
        :return:
        '''
        data = (
            'nms.collector.ex',
            'nms.heartbeat.k:' + devid,
            '{"eventid": "EV_COLLECTOR_HEARTBEAT_ACK","devid": "%s","rptime":"%s"}' % (
                devid, datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        )
        rmq_produce_thread.push(data)

    def _add_timer(self, collectorid):
        '''
        给collector添加超时处理程序
        :param collectorid:
        :return:
        '''
        self._collector[collectorid] = Timer(
            30, self._collector_offline, args=(collectorid,))
        self._collector[collectorid].start()

    def _update_timer(self, collectorid):
        '''
        更新collector超时时间
        :param collectorid:
        :return:
        '''
        # 定时器延后30秒
        self._collector[collectorid].cancel()
        self._collector[collectorid] = Timer(
            30, self._collector_offline, args=(collectorid,))
        self._collector[collectorid].start()

    def _collector_online(self, collectorid, devid):
        from core.heartbeat_msg_handler import online_collector
        online_collector(collectorid, devid)
        # 创建对应collector的监听线程
        if collectorid not in self._thread:
            self._thread[collectorid] = CollectorMQThread('collector_mq_thread_' + devid, {
                "exchange": COLLECTOR_CONSUMER['exchange'],
                "exchange_type": COLLECTOR_CONSUMER['exchange_type'],
                "queue": COLLECTOR_CONSUMER['queue'] + ':' + devid,
                "routing_key": COLLECTOR_CONSUMER['routing_key'] + ':' + devid
            }, devid)
            self._thread[collectorid].start()

    def _collector_offline(self, collectorid):
        from core.heartbeat_msg_handler import offline_collector
        logging.info('[%s] collector offline %s' %
                     (self._name, collectorid))
        # 原先线程保留
        offline_collector(collectorid)


class CollectorMQThread(RMQConsumerThread):
    '''
    本线程监听collector进程发送过来的物理服务器,逻辑服务器,终端消息
    消息会根据来源发送到不同的消息处理线程进行处理
    '''

    def __init__(self, name, mq_arg, moid=''):
        self.logical_msg_thread = BusinessMsgThread(
            'logical_msg_thread_' + moid, 'logical_msg_handler')
        self.physical_msg_thread = BusinessMsgThread(
            'physical_msg_thread_' + moid, 'physical_msg_handler')
        self.terminal_msg_thread = BusinessMsgThread(
            'terminal_msg_thread_' + moid, 'terminal_msg_handler')
        self.terminal_26_msg_thread = BusinessMsgThread(
            'terminal_26_msg_thread_' + moid, 'terminal_26_msg_handler')
        self.terminal_48_msg_thread = BusinessMsgThread(
            'terminal_48_msg_thread_' + moid, 'terminal_48_msg_handler')
        self.logical_msg_thread.start()
        self.physical_msg_thread.start()
        self.terminal_msg_thread.start()
        self.terminal_26_msg_thread.start()
        self.terminal_48_msg_thread.start()
        super().__init__(name, mq_arg)

    def dispatch(self, msg):
        '''
        把消息分发到对应的处理函数
        备注: 会管发送过来的预约会议和实体会议消息会被丢弃
        :param msg:
        :return:
        '''
        msgsrc = msg.get('msgsrc', '')
        devtype = msg.get('devtype', '')
        logger.debug('[%s] msg= %s' % (self._name, msg))
        # 2.6终端类型
        if msgsrc == 'bridge26':
            self.terminal_26_msg_thread.push(msg=msg)
        # 4.8终端类型
        elif msgsrc == 'bridge48':
            self.terminal_48_msg_thread.push(msg=msg)
        # 5.0终端类型
        elif msgsrc == 'mt':
            self.terminal_msg_thread.push(msg=msg)
        # 物理服务器类型
        elif server_type_judgment.is_physical_type(devtype):
            self.physical_msg_thread.push(msg=msg)
        # 逻辑服务器类型
        elif server_type_judgment.is_logical_type(devtype):
            self.logical_msg_thread.push(msg=msg)
        else:
            logger.error(
                '[%s]: cannot find message handler thread, drop msg: %s' % (self._name, str(msg)))


class MeetingMQThread(RMQConsumerThread):
    '''
    本线程监听collector进程发送过来的物理服务器,逻辑服务器,终端消息
    消息会根据来源发送到不同的消息处理线程进行处理
    '''

    def __init__(self, name, mq_arg):
        self.msg_thread = BusinessMsgThread(
            'meeting_msg_thread', 'meeting_msg_handler')

        self.msg_thread.start()
        super().__init__(name, mq_arg)

    def dispatch(self, msg):
        '''
        把消息分发到对应的处理函数
        备注: 会管发送过来的预约会议和实体会议消息会被丢弃
        :param msg:
        :return:
        '''
        self.msg_thread.push(msg=msg)


class InspectMQThread(RMQConsumerThread):
    '''
    巡检监听线程
    '''

    def __init__(self, name, mq_arg):
        from core.inspect_msg_handler import init_inspect
        init_inspect()
        super().__init__(name, mq_arg)

    def dispatch(self, msg):
        from core.inspect_msg_handler import add_inspect, update_inspect, del_inspect
        logger.info('[%s]: msg=%s' % (self._name, msg))
        try:
            func = eval(msg['eventid'])
            if callable(func):
                func(msg['taskid'])
        except Exception as e:
            logger.error(e)


class RMQProduceThread(MsgProcessThread):
    '''
    starter 消息发送线程
    '''

    def __init__(self, name):
        super().__init__(name)

    @retry(tries=3, delay=2, backoff=2, logger=logger)
    @retry(tries=3)
    def connect_to_rmq(self):
        self.connection = pika.BlockingConnection(
            parameters=pika.URLParameters(AMQP_URL)
        )

    @retry(tries=3, delay=2, backoff=2, logger=logger)
    @retry(tries=3)
    def dispatch(self, data):
        '''
        data: 元组, (exchange, routing_key, body)
        '''
        try:
            with self.connection.channel() as c:
                logger.info('[%s] send_msg: %s' % (self._name, data))
                c.basic_publish(*data)
        except Exception:
            self.connect_to_rmq()
            raise Exception('[%s] reconnect to rmq' % self._name)


rmq_produce_thread = RMQProduceThread('mq_produce_thread')
