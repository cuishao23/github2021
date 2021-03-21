import threading
import logging
import json
import queue
from datetime import datetime
from utils.rmq.consumer import ReconnectingConsumer
from config.common import LOGGING, AMQP_URL, MAX_MSG_QUEUE_LEN

logger = logging.getLogger(LOGGING['loggername'])


class RMQConsumerThread(threading.Thread):
    '''
    本线程监听bmc发送的消息: 用户/域/机房/老终端/license
    消息会发送到bmc_msg_thread线程进行处理
    '''

    def __init__(self, name, mq_arg):
        self._mq_arg = mq_arg
        super().__init__(name=name, daemon=True)

    # 重写run方法
    def run(self):
        while True:
            try:
                consumer = ReconnectingConsumer(
                    self._name,
                    exchange=self._mq_arg['exchange'],
                    queue=self._mq_arg['queue'],
                    routing_key=self._mq_arg['routing_key'],
                    exchange_type=self._mq_arg['exchange_type'],
                    amqp_url=AMQP_URL,
                    handler=self.handler)
                consumer.run()
            except Exception as err:
                logger.error(err)

    def handler(self, message):
        try:
            data = json.loads(message.decode('utf-8'))
            if 'rpttime' not in data:
                data['rpttime'] = datetime.now().strftime(
                    '%Y/%m/%d:%H:%M:%S')
            self.dispatch(data)
        except Exception as e:
            logger.error('[%s]: error:%s, msg:%s' % (self._name, str(e), message))

    def dispatch(self, data):
        '''
        将消息分发到具体处理线程
        '''
        raise NotImplementedError(
            'subclasses of RMQThread must provide a dispatch() method')


class MsgProcessThread(threading.Thread):
    '''
    一个绑定了队列的线程, 模拟channel
    push: 向此线程发送消息
    pop: 从此线程队列取出一个消息
    '''

    def __init__(self, name, queue_maxsize=MAX_MSG_QUEUE_LEN):
        self._queue = queue.Queue(queue_maxsize)
        self._do_run = True
        super().__init__(name=name, daemon=True)

    def run(self):
        while self._do_run:
            try:
                msg = self.pop()
            except Exception as e:
                logger.error(e)
            try:
                self.dispatch(msg)
            except Exception as err:
                logger.error(err)

    def dispatch(self, data):
        raise NotImplementedError(
            'subclasses of RMQThread must provide a dispatch() method')

    def get_queue_size(self):
        '''
        获取线程消息队列大小
        :return:
        '''
        return self._queue.qsize()

    def push(self, msg):
        '''
        向此线程发送消息
        :param msg:
        :return:
        '''
        try:
            self._queue.put_nowait(msg)
        except queue.Full:
            logger.error('%s: queue is full, drop msg = %s' %
                         (self._name, msg))

    def pop(self):
        return self._queue.get(block=True)

    def __repr__(self):
        return super().__repr__() + ' qsize=%s' % self.get_queue_size()
