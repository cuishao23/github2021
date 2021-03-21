# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

import functools
import logging
import time
import pika
from config.common import LOGGING

LOGGER = logging.getLogger(LOGGING['loggername'])



class Consumer(object):

    def __init__(self, consumer_name, exchange_name, queue_name, routing_key, handler, exchange_type, amqp_url):

        # 状态
        self.should_reconnect = False
        self.was_consuming = False

        # 参数
        self._consumer_name = consumer_name
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._queue_name = queue_name
        self._routing_key = routing_key
        self._handler = handler

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url
        self._consuming = False
        # In production, experiment with higher prefetch values
        # for higher consumer throughput
        self._prefetch_count = 1

    def connect(self):
        LOGGER.info('[' + self._consumer_name + '] ' + 'Connecting to %s', self._url)
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def close_connection(self):
        self._consuming = False
        if self._connection.is_closing or self._connection.is_closed:
            LOGGER.info('[' + self._consumer_name + '] ' +
                      ' Connection is closing or already closed')
        else:
            LOGGER.info('[' + self._consumer_name + '] ' + 'Closing connection')
            self._connection.close()

    def on_connection_open(self, _unused_connection):
        """
        连接建立后调用

        :param pika.SelectConnection _unused_connection: The connection

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        """
        无法建立连接时处理

        :param pika.SelectConnection _unused_connection: The connection
        :param Exception err: The error

        """
        LOGGER.error('[' + self._consumer_name + '] ' + 'Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        """
        rmq连接断开时, 回调

        :param pika.connection.Connection connection: The closed connection obj
        :param Exception reason: exception representing reason for loss of
            connection.

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('[' + self._consumer_name + '] ' +
                         'Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        """Will be invoked if the connection can't be opened or is
        closed. Indicates that a reconnect is necessary then stops the
        ioloop.

        """
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        """
        声明 channel

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        """
        channel 打开时回调

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange()

    def add_on_channel_close_callback(self):
        """
        添加 rmq 关闭通道时回调

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        """
        rmq 关闭通道时回调

        :param pika.channel.Channel: The closed channel
        :param Exception reason: why the channel was closed

        """
        LOGGER.warning('[' + self._consumer_name + '] ' +
                     'Channel %i was closed: %s', channel, reason)
        self.close_connection()

    def setup_exchange(self):
        """
        设置 exchange

        """
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'Declaring exchange: %s', self._exchange_name)
        self._channel.exchange_declare(
            exchange=self._exchange_name,
            exchange_type=self._exchange_type,
            callback=self.on_exchange_declareok,
            durable=True
            )

    def on_exchange_declareok(self, _unused_frame):
        """
        exchange 声明成功时回调

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame

        """
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'Exchange declared: %s', self._exchange_name)
        self.setup_queue()

    def setup_queue(self):
        """
        声明 queue

        :param str|unicode queue_name: The name of the queue to declare.

        """
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'Declaring queue %s', self._queue_name)
        self._channel.queue_declare(
            queue=self._queue_name, callback=self.on_queue_declareok, durable=True)

    def on_queue_declareok(self, _unused_frame):
        """
        队列声明成功回调

        :param pika.frame.Method _unused_frame: The Queue.DeclareOk frame

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Binding %s to %s with %s', self._exchange_name, self._queue_name,
                    self._routing_key)
        self._channel.queue_bind(
            self._queue_name,
            self._exchange_name,
            routing_key=self._routing_key,
            callback=self.on_bindok)

    def on_bindok(self, _unused_frame):
        """
        绑定成功回调

        :param pika.frame.Method _unused_frame: The Queue.BindOk response frame

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Queue bound: %s', self._queue_name)
        self.set_qos()

    def set_qos(self):
        """
        设置预取计数

        """
        self._channel.basic_qos(
            prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'QOS set to: %d', self._prefetch_count)
        self.start_consuming()

    def start_consuming(self):
        """
        启动消费者
        """
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'Issuing consumer related RPC commands')
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(
            self._queue_name, self.on_message)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        """
        添加 rmq 取消使用时的回调

        """
        LOGGER.debug('[' + self._consumer_name + '] ' +
                  'Adding consumer cancellation callback')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame

        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Consumer was cancelled remotely, shutting down: %r',
                    method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        """
        消息回调

        :param pika.channel.Channel _unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param bytes body: The message body

        """
        try:
            self._handler(body)
        except Exception as e:
            LOGGER.error('[' + self._consumer_name + '] ' +
                       ' on message handler error, %s' % e)
        self._channel.basic_ack(basic_deliver.delivery_tag)

    def stop_consuming(self):
        """
        通知 rmq, 希望停止消费
        """
        if self._channel:
            LOGGER.debug('[' + self._consumer_name + '] ' +
                      'Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(self._consumer_tag, self.on_cancelok)

    def on_cancelok(self, _unused_frame):
        """
        rmq确认后, 关闭channel

        :param pika.frame.Method _unused_frame: The Basic.CancelOk frame

        """
        self._consuming = False
        self.close_channel()

    def close_channel(self):
        """
        关闭 channel
        """
        LOGGER.debug('[' + self._consumer_name + '] ' + 'Closing the channel')
        self._channel.close()

    def run(self):
        """
        运行消费者, 建立连接, 开启事件循环

        """
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.

        """
        if not self._closing:
            self._closing = True
            LOGGER.debug('[' + self._consumer_name + '] ' + 'Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            LOGGER.debug('[' + self._consumer_name + '] ' + 'Stopped')


class ReconnectingConsumer(object):
    '''
    具有自动重连功能的消费者
    '''

    def __init__(self, consumer_name, exchange, queue, routing_key, handler, exchange_type, amqp_url):
        self._reconnect_delay = 0
        self.connect_args = (
            consumer_name, exchange, queue,
            routing_key, handler, exchange_type, amqp_url
        )
        self._consumer = Consumer(*self.connect_args)

    def run(self):
        while True:
            try:
                self._consumer.run()
            except Exception as e:
                LOGGER.error('reconnect RMQ, args=%s, error=%s' %
                             (self.connect_args, e))
            self._maybe_reconnect()

    def _maybe_reconnect(self):
        if self._consumer.should_reconnect:
            self._consumer.stop()
            reconnect_delay = self._get_reconnect_delay()
            LOGGER.debug('Reconnecting after %d seconds', reconnect_delay)
            time.sleep(reconnect_delay)
            self._consumer = Consumer(*self.connect_args)

    def _get_reconnect_delay(self):
        if self._consumer.was_consuming:
            self._reconnect_delay = 0
        else:
            self._reconnect_delay += 1
        if self._reconnect_delay > 30:
            self._reconnect_delay = 30
        return self._reconnect_delay
