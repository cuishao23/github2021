from retry import retry
from threading import Thread
import os
import json
import pika
import sys
sys.path.append(
    '/opt/mcu/nms_starter/starter_python3/lib/python3.5/site-packages')

AMQP_URL = 'amqp://{user}:{password}@{host}:{port}/'.format(
    user="dev",
    password="dev",
    host="127.0.0.1",
    port=5672
)


class StarterTest():
    '''
    发送rmq测试信息
    test_type: 0: 自动测试, 1: 单文件测试
    '''

    def __init__(self, test_type):
        self.test_type = test_type
        self.connect_to_rmq()
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.single_test_file = os.path.join(self.path, 'single_test.json')
        self.auto_test_dir = os.path.join(self.path, 'auto')

    @retry(delay=1)
    def connect_to_rmq(self):
        self.connection = pika.BlockingConnection(
            parameters=pika.URLParameters(AMQP_URL)
        )

    @retry(delay=1)
    def dispatch(self, exchange, routing_key, msg):
        try:
            with self.connection.channel() as c:
                print('发送到:%s, routing_key=%s' % (exchange, routing_key))
                c.basic_publish(exchange, routing_key, msg)
        except Exception:
            self.connect_to_rmq()
            raise Exception('reconnect to rmq')

    def run(self):
        if self.test_type == 1:
            print('开始单文件测试')
            with open(self.single_test_file) as f:
                data = json.load(f)
            for info in data:
                print(info['name'])
                msg = input("是否执行[y]?")
                if msg in ('n', 'N', 'exit', 'q', 'Q'):
                    continue
                self.dispatch(info['exchange'],
                              info['routing_key'], json.dumps(info['msg']))

            print('测试结束')
        else:
            print('开始批量测试')
            while True:
                pass


if __name__ == "__main__":
    test = StarterTest(1)
    test.run()
