import webbrowser
import time
import sys

# open results file (contains stocks from market_scanner.py output)
with open("results.txt", "r") as f:
	results = f.read().splitlines()

answer = input("Are you sure you want to open {} tabs in a new browser window? [y/N]: ".format(len(results)))

if answer.lower() == 'y':
	first = True 
	for stock in results:
		if first:
			#if you want to open in you current browser, use .open() instead
			webbrowser.open_new("http://robinhood.com/stocks/{}".format(stock))
			first = False
			#increase this time if they don't all load in the same new browser
			time.sleep(1)
		else:
			webbrowser.open("http://robinhood.com/stocks/{}".format(stock))
else:
	sys.exit()
