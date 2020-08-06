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

  ## this will go back to false when we move to production
  app.config["DEBUG"] = True

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

        #The forms have limits (& regex patterns), but users can type in whatever number
        # (although it should at least always be numeric)
        # On mobile, the telephone keypad should open up
        # On desktop, they can enter negative signs, periods, and 'e'
        # ... it doesnt check if it's a valid expression however :[

        month_cut = request.form.get('month_cutoff')
        try:
          month_cut = int(month_cut)
        except:
          print(f'month cutoff {month_cut} is a bad number')
          month_cut = 6
        
        month_cut = max(min(month_cut, 12), 1)        # 12 > month_cut > 1
#----------
        day_cut = request.form.get('day_cutoff')
        try:
          day_cut = int(day_cut)
        except:
          print(f'day cutoff {day_cut} is a bad number')
          day_cut = 3

        day_cut = max(min(day_cut, 31), 1)           # 31 > day_cut > 1
#----------
        std_cut = request.form.get('std_cutoff')
        try:
          std_cut = int(std_cut) # maybe make this not an int
        except:
          print(f'std cutoff {std_cut} is a bad number')
          std_cut = 2

        std_cut = max(min(std_cut, 10), 1)            # 10 > std_cut > 1
#----------
      stonk_search = mainObj(_month_cuttoff=month_cut,_day_cuttoff=day_cut,_std_cuttoff=std_cut)
      stonks = stonk_search.main_func(doFilter=True)
      return render_template('dynamic.html', stonks=stonks, month_cut=month_cut, day_cut=day_cut, std_cut=std_cut, update_time=stonk_search.updated_at)

  if _refresh:
    print('hi')
    reThread = Thread(target=refresh_wrapper_wrapper, daemon=True)
    reThread.start()

  return app

if __name__ == "__main__":
    AUTO_REFRESH = False

    stonk_search = mainObj(_month_cuttoff=6,_day_cuttoff=3,_std_cuttoff=4)
    stonks = stonk_search.main_func(doFilter=True)

    app = create_flask_app(AUTO_REFRESH)
    app.run(host='0.0.0.0',port='5000', debug=True, use_reloader=False, use_evalex=False) # run the app on LAN
    #app.run() # run the app on your machine
