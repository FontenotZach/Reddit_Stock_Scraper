import praw
from ftplib import FTP
from Ticker import *
from Comment_Info import *
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import xlwt
from xlrd import open_workbook
from xlutils.copy import copy
from xlwt import Workbook
import datetime
import time
import pandas as pd
import numpy as np

def get_post_comments(post, more_limit=50):
    comments = []
    post.comments.replace_more(limit=more_limit)
    for top_level in post.comments:
        comments.extend(process_comment(top_level))
    return comments

def process_comment(comment, depth=0):
    yield Comment_Info(comment.body, depth, comment.score)
    for reply in comment.replies:
        yield from process_comment(reply, depth + 1)

# generates list of tuples as (Ticker:score_to_add) for a comment
def comment_score(comment):

    remove_links(comment)

    if check_all_capitalized(comment):
        return

    clean_comment(comment)

    removed_symbol_present = check_removed(comment)

    # extract symbols
    symbols_present = extract_symbols(comment)
    # calulcate scores
    for ticker in symbols_present:
        score = 1 + comment.score * 0.05
        ticker.score = score
    return symbols_present


def check_removed(comment):

    symbol_reader = open('removed.txt', 'r')
    removed_symbols = symbol_reader.readlines()

    symbols_present = []

    for symbol in removed_symbols:
        symbol = symbol.rstrip()
        check_symbol = '$' + symbol + ' '
        if comment.body.find(check_symbol) >= 0:
            t = Ticker(symbol)
            symbols_present.append(t)

    return symbols_present

def extract_symbols(comment):

    comment.body = re.sub(r'[$]', '', comment.body)
    symbol_reader = open('symbols.txt', 'r')
    all_symbols = symbol_reader.readlines()

    symbols_present = []

    for symbol in all_symbols:
        symbol = symbol.rstrip()
        padded_symbol = ' ' + symbol + ' '
        if comment.body.find(padded_symbol) >= 0:
            t = Ticker(symbol)
            symbols_present.append(t)

    return symbols_present



def clean_comment(comment):
    # stop_word_reader = open('stopwords.txt', 'r')
    # stop_words = stop_word_reader.readlines()

    # remove non letters, words longer than 6 characters, normal words
    comment.body = re.sub(r'[^$\w\s]+', ' ', comment.body)
    comment.body = re.sub(r'[0-9]', ' ', comment.body)
    comment.body = re.sub(r'\b\w{7,}\b', ' ', comment.body)
    comment.body = re.sub(r'[A-Z]?[\']?[a-z]{1,}', ' ', comment.body)
    comment.body = ' ' + comment.body + ' '
    comment.body = re.sub(r'\s{2,}', ' ', comment.body)
    # maybe check for uppercase stop words
    # for word_to_replace in stop_words:
    #     word_to_replace = word_to_replace.rstrip()
    #     comment.body = re.sub(r"\b{}\b".format(word_to_replace), ' ', comment.body)

    return

def remove_links(comment):
    comment.body = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    comment.body = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    return

def check_all_capitalized(comment):
    all_cap = False

    num_letters = len(comment.body)
    cap_only = re.sub(r'[^A-Z]+', '', comment.body)
    num_cap = len(cap_only)

    if num_letters > 0:
        if num_cap / num_letters > 0.2  or num_cap > 20:
            all_cap = True
    return all_cap


def retrieve_stock_symbols():
    file_name = 'nasdaqlisted.txt'
    ftp = FTP('ftp.nasdaqtrader.com')
    ftp.login()
    ftp.cwd('SymbolDirectory')
    with open(file_name, 'wb') as f:
            ftp.retrbinary('RETR ' + file_name, f.write)
    file_name = 'otherlisted.txt'
    with open(file_name, 'wb') as f:
            ftp.retrbinary('RETR ' + file_name, f.write)

    file_writer = open('symbols.txt', 'a')
    nasdaq_reader = open('nasdaqlisted.txt', 'r')
    other_reader = open('otherlisted.txt', 'r')

    nasdaq_symbols = nasdaq_reader.readlines()
    other_symbols = other_reader.readlines()

    for symbol in nasdaq_symbols:
        trimmed_symbol = re.sub(r'[|].*', '', symbol)
        file_writer.write(trimmed_symbol)

    for symbol in other_symbols:
        trimmed_symbol = re.sub(r'[|].*', '', symbol)
        file_writer.write(trimmed_symbol)

    file_writer.close()

def get_time():

    date_time = datetime.datetime.now()

    return date_time

def get_index():
    # enter start date here
    t = datetime.datetime(2021, 7, 28)
    current_time = get_time()
    dif = current_time - t

    total_hours = dif.total_seconds() / 3600

    if total_hours < 0:
        total_hours = 0

    return total_hours


def wait_for_next_hour():

    entry_time = get_time()
    current_time = get_time()

    entry_hour = entry_time.hour
    current_hour = current_time.hour

    while entry_hour == current_hour:
        time.sleep(20)
        current_time = get_time()
        current_hour = current_time.hour


def write_to_csv(tickers, set, sub):

    frame = []
    headers = ['dataset', 'symbol', 'score']

    for ticker in tickers:
        if ticker.score <= 0:
            break
        row = ['Score', ticker.symbol, ticker.score]
        frame.append(row)


    df = pd.DataFrame(frame, columns=headers)
    df.to_csv('Data/Reddit-Stock-Scraper_'+ sub + '_' + set + '.csv', index=False)


def write_to_excel(tickers, set, sub):
    wb = Workbook()
    WSB_Data = wb.add_sheet('WSB_Data')

    WSB_Data.write(0,0, 'WSB Scrape Data')
    WSB_Data.write(2, 0, 'Symbol')
    WSB_Data.write(2, 1, 'Score')

    row = 3

    for ticker in tickers:
        if ticker.score <= 0:
            break
        WSB_Data.write(row, 0, ticker.symbol)
        WSB_Data.write(row, 1, ticker.score)
        row+=1

    row = 1

    wb.save('Data/Reddit-Stock-Scraper_'+ sub + '_' + set + '.xls')
