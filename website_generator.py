import flask
from flask_flatpages import FlatPages
from flask_frozen import Freezer
from flask import Flask, request, send_from_directory, render_template
from shutil import copyfile
import os
import shutil
import numpy
from market_scanner import mainObj

# this is used by me AUTOMATICALLY to update the web page you can find at: https://sampom100.github.io/UnusualVolumeDetector/

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
    return render_template('template.html', stonks=stonks)


if __name__ == "__main__":
    os.system('git fetch')
    stonk_search = mainObj()
    stonks = stonk_search.main_func()
    stonks = stonks[:15]
    freezer.freeze()
    copyfile('build/index.html', 'index.html')
    shutil.rmtree('build/')
    # I'm lazy :)
    os.system('git add .')
    os.system('git commit -m "updated website"')
    os.system('git push origin master')
    # print(stonks)
    # app.run(host='0.0.0.0', port='5000')  # run the app on LAN
    # app.run()  # run the app on your machine
