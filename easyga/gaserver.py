#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用来作为接受google统计上报的server端
通过zmq通道
"""

import pickle
import functools
import logging
import logging.config

import zmq

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
    _port = None

    def __init__(self, port):
        self._port = port

    @record_exception
    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % self._port)

        while True:
            try:
                message = socket.recv()
            except Exception, e:
                logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())
                continue

            #logger.debug(message)

            handle_message(message)

            # 必须要调用send，否则zmq会报错 ZMQError: Operation cannot be accomplished in current state
            socket.send('ok')
