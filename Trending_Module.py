import csv
import numpy as np
import pandas as pd
import datetime
import os
import glob
from Ticker import *
from operator import attrgetter
import statistics
from Util import *



# Trending_Module.py
# Seperate process from scraper which will be ran as needed
# Takes CSV input (one single column representing mention score for that hour)
# Outputs a list of Ticker objects with trending score calculated


# inout: ticker and list of hourly scraper data e.g. {4, 2, 5, 14, 20, 44...}
# output: calulcate trending score and enter into ticker.trending_score attribute
def calc_trending_score(ticker, x):

    current_index = int(get_index())
    missing_vals = current_index - x.size + 1
    for i in range(0, missing_vals):
        x = np.append(x, [0])

    if x.size > 1:
        y = []
        for i in range(0, x.size):
            y.append(i)
        x_mean = mean(x)
        y_mean = mean(y)
        covari = covariance(x, x_mean, y, y_mean)
        vari = statistics.variance(x)
        if vari == 0:
            m = 0
        else:
            m =  covari / vari
    else:
        m = 0
    return m

# Calculate the mean value of a list of numbers
def mean(values):
	return sum(values) / float(len(values))

# Calculate the variance of a list of numbers
def variance(values, mean):
	return sum([(x - mean)**2 for x in values])

# Calculate covariance between x and y
def covariance(x, mean_x, y, mean_y):
	covar = 0.0
	for i in range(len(x)):
		covar += (x[i] - mean_x) * (y[i] - mean_y)
	return covar

# Ticker is relevant if mentioned 10+ times in any hour within the past day
def check_relevancy(x):

    relevant = False
    cutoff = 15

    current_index = int(get_index())
    missing_vals = current_index - x.size + 1
    if missing_vals < 24:
        for i in range(0, missing_vals):
            x = np.append(x, [0])

        for i in range(x.size - 24, x.size):
            if x[i] >= cutoff:
                relevant = True

    return relevant

if __name__ == '__main__':
    data_path = './Data/stream'

    tickers = []

    for filename in glob.glob(os.path.join(data_path, '*.csv')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:

            symbol = filename.split('/')[4].split('_')[0]
            ticker = Ticker(symbol)

            data = np.loadtxt(f)
            if check_relevancy(data):
                trending_score = calc_trending_score(ticker, data)
                result = (ticker.symbol, trending_score)
                tickers.append(result)

    tickers.sort(key=lambda x: x[1], reverse = True)
    headers = ['source', 'symbol', 'trending score']
    df = pd.DataFrame(tickers, columns=headers)
    df.to_csv('Data/trending.csv', index=False)
