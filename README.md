# Unusual Volume Detector

This scans every ticker on the market, gets their last 5 months of volume history, and alerts you when a stock's volume exceeds 10 standard deviations from the mean within the last 3 days. (these numbers are all adjustable).  Helps find anomalies in the stock market


## How to run this:

If you need to install python: https://www.python.org/downloads/

Download my script:
```
$ git clone https://github.com/SamPom100/UnusualVolumeDetector.git
```

Get packages
```
$ pip install -r requirements.txt
```

Run the app
```
$ python3 market_scanner.py
```

-you can also graph any ticker's volume in grapher.py

## Controlling the Script
-[Line 17](https://github.com/SamPom100/UnusualVolumeDetector/blob/master/market_scanner.py#L17) controls the amount of months of historical volume the script gets

-[Line 75](https://github.com/SamPom100/UnusualVolumeDetector/blob/master/market_scanner.py#L75) controls the amount of days before today that it will alert you

-[Line 84](https://github.com/SamPom100/UnusualVolumeDetector/blob/master/market_scanner.py#L17) controls the number of standard deviations away from the mean volume



![j67nuj3cl0e51](https://user-images.githubusercontent.com/28206070/88943805-8d1ea080-d251-11ea-81ed-04138e21bf1f.png)

![ue395lbgl0e51](https://user-images.githubusercontent.com/28206070/88943804-8d1ea080-d251-11ea-8c03-3f42da8849f6.png)

![s9jtygygl0e51](https://user-images.githubusercontent.com/28206070/88943801-8c860a00-d251-11ea-833b-8e7685360ab2.png)
