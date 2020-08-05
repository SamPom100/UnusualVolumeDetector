import flask
from flask import Flask, request, send_from_directory, render_template
import os
import numpy

from market_scanner import mainObj
from threading import Timer, Lock, Thread
import queue

UPDATE_FREQ = 5

month_cut = 6
day_cut = 3
std_cut = 4

stonk_search = mainObj(_month_cuttoff=month_cut,_day_cuttoff=day_cut,_std_cuttoff=std_cut)
stonks = []

dataLock = Lock()

def create_flask_app(_refresh=False):
  app = flask.Flask(__name__, static_url_path='')
  app.config["DEBUG"] = False

  SECRET_KEY = os.getenv('SECRET_KEY', 'deditated_wam') #pulls SECRET_KEY from env var, else sets as 'detitaded_wam'
  app.config['SECRET_KEY'] = SECRET_KEY

  def refresh_thread(month_cut, day_cut, std_cut):
    global stonks, stonk_search

    results = mainObj(_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=2)
    with dataLock:
      stonks = stonk_search.main_func(doFilter=True)

  def refresh_wrapper(month_cut,day_cut,std_cut):
    rThread = Thread(target=refresh_thread, args=(month_cut,day_cut,std_cut))

    rThread.start()
    rThread.join()

  def refresh_wrapper_wrapper(): #we have to go deeper
    global UPDATE_FREQ, month_cut, day_cut, std_cut
    while True:
      refresher_loop = Timer(interval=UPDATE_FREQ*60, function=refresh_wrapper, args=(month_cut,day_cut,std_cut))
      refresher_loop.start()
      refresher_loop.join()



  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'localhost*,192.168.*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  @app.route('/', methods=['GET'])
  def home():
    if _refresh:
      return render_template('dynamicRefresh.html', stonks=stonks, month_cut=6, day_cut=3, std_cut=2, update_time=stonk_search.updated_at)
    else:
      return render_template('dynamic.html', stonks=stonks, month_cut=6, day_cut=3, std_cut=2, update_time=stonk_search.updated_at)

  @app.route('/reload/', endpoint="reload", methods=["POST"]) 
  def refresh():
      if request.method == "POST":
        month_cut = int(request.form.get('month_cutoff'))
        #didn't want to do this in JS lmao
        #The forms have limits, but users can type in whatever number
        #It's me, yandaredev
        if month_cut > 12:
          month_cut = 12
        if month_cut < 1:
          month_cut = 1
        day_cut = int(request.form.get('day_cutoff'))
        if day_cut > 30:
          day_cut = 30
        if day_cut < 1:
          day_cut = 1
        std_cut = int(request.form.get('std_cutoff'))
        if std_cut > 10:
          std_cut = 10
        if std_cut < 1:
          std_cut = 1
      stonk_search = mainObj(_month_cuttoff=month_cut,_day_cuttoff=day_cut,_std_cuttoff=std_cut)
      stonks = stonk_search.main_func(doFilter=True)
      return render_template('dynamic.html', stonks=stonks, month_cut=month_cut, day_cut=day_cut, std_cut=std_cut, update_time=stonk_search.updated_at)

  if _refresh:
    print('hi')
    reThread = Thread(target=refresh_wrapper_wrapper, daemon=True)
    reThread.start()

  return app

if __name__ == "__main__":
    AUTO_REFRESH = True

    stonk_search = mainObj(_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=4)
    stonks = stonk_search.main_func(doFilter=True)

    app = create_flask_app(AUTO_REFRESH)
    app.run(host='0.0.0.0',port='5000') # run the app on LAN
    #app.run() # run the app on your machine
