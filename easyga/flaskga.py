# -*- coding: utf-8 -*-

"""
flask插件，绑定之后可以自动给本地的gaserver发送数据
要求配置:
    GA_ID : Google分析的跟踪ID
    GASERVER_PORT : GAServer的启动端口
    GA_USE_GEVENT : 是否使用了gevent(True/False)，默认为False
"""
import pickle

from flask import current_app, request, session
from pyga.requests import Tracker, Page, Session, Visitor


class FlaskGA(object):
    _context = None
    _socket = None
    _ga_id = None
    _gaserver_port = None
    _ga_use_gevent = False

    def __init__(self, app):
        if app:
            self.init_app(app)

    def init_app(self, app):
        """
        绑定app
        """
        self._ga_id = app.config['GA_ID']
        self._gaserver_port = app.config['GASERVER_PORT']
        self._ga_use_gevent = app.config.get('GA_USE_GEVENT', False)

        if not self._ga_use_gevent:
            import zmq
        else:
            import zmq.green as zmq

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect("tcp://localhost:%(port)s" % dict(port=self._gaserver_port))

        @app.before_request
        def send_ga_data():
            try:
                tracker = Tracker(self._ga_id, request.host)
                session = Session()
                page = Page(request.path)
                visitor = Visitor()
                visitor.ip_address = request.remote_addr

                self.send_data_to_gaserver(tracker, 'track_pageview', (page, session, visitor))
            except Exception, e:
                current_app.logger.error('exception occur. msg[%s], traceback[%s]', str(e), __import__('traceback').format_exc())

    def send_data_to_gaserver(self, caller, funcname, args=None, kwargs=None):
        """
        可以在网站中调用
        """
        if not self._ga_use_gevent:
            import zmq
        else:
            import zmq.green as zmq

        data = dict(
            caller=caller,
            funcname=funcname,
            args=args or [],
            kwargs=kwargs or {},
        )

        self._socket.send(pickle.dumps(data))
        # 还需要recv，貌似不recv的话，会出问题
        self._socket.recv()
