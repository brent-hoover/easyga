# -*- coding: utf-8 -*-
import zmq
import pickle
from pyga.requests import Tracker, Page, Session, Visitor, Config

config = Config()
tracker = Tracker('UA-32788866-33', 'appspot.liuyiwo.com', config)
session = Session()
visitor = Visitor()
page = Page('/new')
visitor.ip_address = '194.54.176.100'
#tracker.track_pageview(page, session, visitor)

context = zmq.Context()

#  Socket to talk to server
print "Connecting to hello world server..."

port = 7500

socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%(port)s" % dict(port=port))

#  Do 10 requests, waiting each time for a response
for request in range (1,1000):
    data = dict(
        caller=tracker,
        funcname='track_pageview',
        args=(page, session, visitor),
        kwargs=None
    )
    print "Sending request ", request,"..."
    socket.send (pickle.dumps(data))
    print "Sended request ", request,"..."

    #  Get the reply.
    message = socket.recv()
    print "Received reply ", request, "[", message, "]"
