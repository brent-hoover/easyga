# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '../')

from flask import Flask
from flaskga import FlaskGA

DEBUG = True

GA_ID = 'UA-32788866-33'
GASERVER_PORT = 5555

app = Flask(__name__)
app.config.from_object(__name__)

fga = FlaskGA(app)


@app.route('/ok')
def ok():
    return u'ok'


if __name__ == '__main__':
    app.run()
