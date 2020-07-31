import os
import time
import yfinance as yf
import dateutil.relativedelta
from datetime import date
import datetime
import numpy as np
import sys
from stocklist import NasdaqController
from tqdm import tqdm
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import configparser
import ast

# Desired anomaly standard deviation cuttoff
standard_deviation = 10

# Set to -1 to parse all
parse_up_to = -1

# The file to output tickers to
ouput_file = "tickers.txt"

# Read email configuration
configParser = configparser.RawConfigParser()   
configFilePath = r'email_config.txt'
configParser.read(configFilePath)
email_enabled = configParser.get('email-config', 'enabled')
server = ast.literal_eval(configParser.get('email-config', 'server'))
from_email = ast.literal_eval(configParser.get('email-config', 'from_email'))
password = ast.literal_eval(configParser.get('email-config', 'password'))
to_emails = ast.literal_eval(configParser.get('email-config', 'to_emails'))

class mainObj:
    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = COMMASPACE.join(to_emails)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Today's Tickers"
        msg.attach(MIMEText("View the attachment for today's tickers."))
        with open(ouput_file, "rb") as f:
            part = MIMEApplication(
                f.read(),
                Name=basename(ouput_file)
            ) 
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(ouput_file)
        msg.attach(part)
        smtp = smtplib.SMTP(server)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(from_email, password)
        smtp.sendmail(from_email, to_emails, msg.as_string())
        smtp.close()

    def getData(self, ticker):
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=5)
        sys.stdout = open(os.devnull, "w")
        data = yf.download(ticker, pastDate, currentDate)
        sys.stdout = sys.__stdout__
        return data[["Volume"]]

    def find_anomalies(self, data, cutoff):
        anomalies = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        indexs = data[data['Volume'] > upper_limit].index.tolist()
        outliers = data[data['Volume'] > upper_limit].Volume.tolist()
        index_clean = [str(x)[:-9] for x in indexs]
        d = {'Dates': index_clean, 'Volume': outliers}
        return d

    def find_anomalies_two(self, data, cutoff):
        indexs = []
        outliers = []
        data_std = np.std(data['Volume'])
        data_mean = np.mean(data['Volume'])
        anomaly_cut_off = data_std * cutoff
        upper_limit = data_mean + anomaly_cut_off
        data.reset_index(level=0, inplace=True)
        for i in range(len(data)):
            temp = data['Volume'].iloc[i]
            if temp > upper_limit:
                indexs.append(str(data['Date'].iloc[i])[:-9])
                outliers.append(temp)
        d = {'Dates': indexs, 'Volume': outliers}
        return d

    def custom_print(self, d, tick):
	    with open(ouput_file, "a") as f:
	        f.write("*******  " + tick.upper() + "  *******\n")
	        f.write("Ticker is: "+tick.upper()+"\n")
	        for i in range(len(d['Dates'])):
	        	str1 = str(d['Dates'][i])
	        	str2 = str(d['Volume'][i])
	        	f.write(str1 + " - " + str2+"\n")
	        f.write("*********************\n\n\n")

    def days_between(self, d1, d2):
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def main_func(self, cutoff):
    	open(ouput_file, "w").close()
    	StocksController = NasdaqController(True)
    	list_of_tickers = StocksController.getList()
    	currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
    	start_time = time.time()
    	count = 0
    	for x in tqdm(list_of_tickers):
    		if parse_up_to > -1 and count == parse_up_to:
    			break
    		d = (self.find_anomalies_two(self.getData(x), cutoff))
    		if d['Dates']:
    			for i in range(len(d['Dates'])):
    				if self.days_between(str(currentDate)[:-9], str(d['Dates'][i])) <= 3:
    					self.custom_print(d, x)
    		count += 1

    	if email_enabled == "true":
    		self.send_email()
    	print("\n\n\n\n--- this took %s seconds to run ---" % (time.time() - start_time))

# run time around 50 minutes for every single ticker.
mainObj().main_func(standard_deviation)
