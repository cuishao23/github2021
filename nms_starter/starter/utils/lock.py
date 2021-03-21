import threading
import functools


class ReadWriteLock(object):
    '''
    读写锁,可以有多个线程同时读,但是有一个线程写的时候, 其他线程既不能读也不能写, 会排队
    '''

    def __init__(self):
        self.__monitor = threading.Lock()
        self.__exclude = threading.Lock()
        self.readers = 0

    def acquire_read(self):
        with self.__monitor:
            self.readers += 1
            if self.readers == 1:
                self.__exclude.acquire()

    def release_read(self):
        with self.__monitor:
            self.readers -= 1
            if self.readers == 0:
                self.__exclude.release()

    def acquire_write(self):
        self.__exclude.acquire()

    def release_write(self):
        self.__exclude.release()


def synchronized(func):

    func.__lock__ = threading.Lock()

    @functools.wraps(func)
    def lock_func(*args, **kwargs):
        with func.__lock__:
            return func(*args, **kwargs)

    return lock_func
