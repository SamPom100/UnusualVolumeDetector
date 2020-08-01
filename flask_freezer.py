import flask
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask import Flask, request, send_from_directory, render_template

import numpy

from market_scanner import mainObj

app = flask.Flask(__name__, static_url_path='')
app.config["DEBUG"] = False
app.config['SECRET_KEY'] = 'deditaded wam'
pages = FlatPages(app)
freezer = Freezer(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'localhost*,192.168.*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/', methods=['GET'])
def home():
    return render_template('index_temp.html', stonks=stonks)


if __name__ == "__main__":
    stonk_search = mainObj()
    stonks = stonk_search.main_func(10)
    # print(stonks)
    # app.run(host='0.0.0.0', port='5000')  # run the app on LAN
    # app.run()  # run the app on your machine
    freezer.freeze()
