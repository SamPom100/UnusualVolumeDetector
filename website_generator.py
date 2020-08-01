import flask
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask import Flask, request, send_from_directory, render_template
from shutil import copyfile
import os
import shutil
import numpy
from market_scanner import mainObj

# this is used by me to generate the web page you can find at: https://sampom100.github.io/UnusualVolumeDetector/

app = flask.Flask(__name__, static_url_path='')
app.config["DEBUG"] = False

SECRET_KEY = os.getenv('SECRET_KEY', 'more_deditated_wam') #pulls SECRET_KEY from env var, else sets as 'more_detitaded_wam'
app.config['SECRET_KEY'] = SECRET_KEY

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
    return render_template('template.html', stonks=stonks)


if __name__ == "__main__":
    stonk_search = mainObj()
    stonks = stonk_search.main_func()
    freezer.freeze()
    copyfile('build/index.html', 'index.html')
    shutil.rmtree('build/')
