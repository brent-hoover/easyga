#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
用来作为接受google统计上报的server端
通过zmq通道
"""

import os
from optparse import OptionParser
import os.path as op
import logging
import logging.config

from gaserver import GAServer

logger = logging.getLogger('default')

DEV_ENV = 'DEV_ENV' in os.environ and os.environ['DEV_ENV'] == '1'

# 日志
# 为了保证邮件只有在正式环境发送
class RequireDebugOrNot(logging.Filter):
    _need_debug = False

    def __init__(self, need_debug, *args, **kwargs):
        super(RequireDebugOrNot, self).__init__(*args, **kwargs)
        self._need_debug = need_debug
        
    def filter(self, record):
        return DEV_ENV if self._need_debug else not DEV_ENV


FILE_MODULE_NAME = op.splitext(op.basename(__file__))[0]

MONITORS = ['xmonitor@qq.com']

LOG_FILE_PATH = "/tmp/gaserver.log"

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
        },
    },

    'filters': {
        'require_debug_false': {
            '()': RequireDebugOrNot,
            'need_debug': False,
        },
        'require_debug_true': {
            '()': RequireDebugOrNot,
            'need_debug': True,
        },
    },

    'handlers': {
        'mail': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.SMTPHandler',
            'formatter': 'standard',
            'filters': ['require_debug_false'],
            'mailhost': 'smtp.qq.com',
            'fromaddr': 'xmonitor@qq.com',
            'toaddrs': MONITORS,
            'subject': '[supervisor-%s]Attention!' % FILE_MODULE_NAME,
            'credentials': ('xmonitor', 'xmr2013'),
        },
        'rotating_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'filters': ['require_debug_true'],
        },
    },

    'loggers': {
        'default': {
            'handlers': ['console', 'rotating_file', 'mail'],
            'level': 'DEBUG',
            'propagate': False
        },
        'gaserver': {
            'handlers': ['console', 'rotating_file', 'mail'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


def build_parser():
    parser = OptionParser(usage="Usage: %prog [options]")
    parser.add_option("-p", "--port", dest="port", help="bind port", action="store")
    return parser


def configure_logging():
    logging.config.dictConfig(LOGGING)

 
def run_gaserver():
    configure_logging()

    parser = build_parser()
    options, system = parser.parse_args()
 
    prog = GAServer(options.port)

    logger.info("Running GAServer on %(port)s" % dict(port=options.port))
    prog.run()
 
if __name__ == '__main__':
    run_gaserver()
