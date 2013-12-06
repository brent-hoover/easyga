#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用来作为接受google统计上报的server端
通过zmq通道。
参考网址: http://learning-0mq-with-pyzmq.readthedocs.org/en/latest/pyzmq/pyzmq.html
"""

import pickle
import functools
import logging
import logging.config

logger = logging.getLogger('gaserver')


def record_exception(func):
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())
            return None

    return func_wrapper


@record_exception
def handle_message(message):
    data = pickle.loads(message)

    caller = data.get('caller', None)
    funcname = data.get('funcname', None)
    args = data.get('args', []) or []
    kwargs = data.get('kwargs', {}) or {}

    return getattr(caller, funcname)(*args, **kwargs)


class GAServer(object):
    _use_gevent = False
    _port = None

    def __init__(self, port, use_gevent=False):
        self._port = port
        self._use_gevent = use_gevent

    @record_exception
    def run(self):
        if not self._use_gevent:
            import zmq
        else:
            import zmq.green as zmq

        context = zmq.Context()
        socket = context.socket(zmq.PAIR)
        socket.bind("tcp://*:%s" % self._port)

        while True:
            try:
                message = socket.recv()
                logger.debug("msg len: %s" % len(message))
                # 先直接返回，反正那边并不关心成功失败
                # client-server 模式下. 必须要调用send，否则zmq会报错 ZMQError: Operation cannot be accomplished in current state
                # pair 模式下，不需要调用send
                # socket.send('ok')
            except Exception, e:
                logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())
                continue

            #logger.debug(message)
            handle_message(message)
