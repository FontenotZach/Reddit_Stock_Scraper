import csv
import numpy as np
import pandas as pd
import datetime
import os
import glob
from Ticker import *

# Trending_Module.py
# Seperate process from scraper which will be ran as needed
# Takes CSV input (one single column representing mention score for that hour)
# Outputs a list of Ticker objects with trending score calculated


# inout: ticker and list of hourly scraper data e.g. {4, 2, 5, 14, 20, 44...}
# output: calulcate trending score and enter into ticker.trending_score attribute
def calc_trending_score(ticker, data):
    # logic to calculate trending score
    ticker.trending_score = -1


if __name__ == '__main__':

    # Test with investing stream data for lighter load
    path_wsb = '.\\Data\\stream\\wallstreetbets'
    path_inv = '.\\Data\\stream\\investing'

    tickers = []

    for filename in glob.glob(os.path.join(path_wsb, '*.csv')):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:

            symbol = filename.split('\\')[4].split('_')[0]
            ticker = Ticker(symbol)

            data = pd.read_csv(f)

            calc_trending_score(ticker, data)

            result = (ticker.symbol, ticker.trending_score)

            tickers.append(result)

    tickers.sort(key = attrgetter('trending_score'), reverse = True)
    headers = ['symbol', 'trending score']
    df = pd.DataFrame(tickers, columns=headers)
    df.to_csv('Data\\trending.csv', index=False)
