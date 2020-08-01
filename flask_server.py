import flask
from flask import Flask, request, send_from_directory, render_template
import os
import numpy

from market_scanner import mainObj

app = flask.Flask(__name__, static_url_path='')
app.config["DEBUG"] = False

SECRET_KEY = os.getenv('SECRET_KEY', 'deditated_wam') #pulls SECRET_KEY from env var, else sets as 'detitaded_wam'
app.config['SECRET_KEY'] = SECRET_KEY



@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', 'localhost*,192.168.*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/', methods=['GET'])
def home():
    return render_template('dynamic.html', stonks=stonks)

if __name__ == "__main__":
    stonk_search = mainObj()
    stonks = stonk_search.main_func()

    app.run(host='0.0.0.0',port='5000') # run the app on LAN
    #app.run() # run the app on your machine
