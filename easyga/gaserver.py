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
            logger.fatal('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())
            return None

    return func_wrapper


@record_exception
def handle_message(message):
    data = pickle.loads(message)

    return getattr(data['caller'], data['funcname'])(*data['args'], **data['kwargs'])


class GAServer(object):
    _port = None

    def __init__(self, port):
        self._port = port

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % self._port)

        while True:
            message = socket.recv()

            handle_message(message)
