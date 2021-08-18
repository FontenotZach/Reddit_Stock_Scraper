from ftplib import FTP
import re
import os
import datetime
import time
import pathlib

from Ticker import *
from Comment_Info import *

debug = False

# Reads the sql database connection configuration information from the provided ini file
def get_sql_config():
    db = {}

    db['host'] = os.getenv('SQL_HOST')
    db['database'] = os.getenv('SQL_DB')
    db['user'] = os.getenv('SQL_USER')
    db['password'] = os.getenv('SQL_PASSWORD')

    return db

#TODO: This seems to not do much, but take a long time to do so
def get_post_comments(post, more_limit=50):
    if debug:
        print(f'Util.py: Getting comments from post {post}')
    comments = []
    post.comments.replace_more(limit=more_limit)
    for top_level in post.comments:
        if debug:
            print(f'Util.py: extending from {top_level}')
        comments.extend(process_comment(top_level))
    return comments

#TODO
def process_comment(comment, depth=0):
    yield Comment_Info(comment.body, depth, comment.score)
    for reply in comment.replies:
        yield from process_comment(reply, depth + 1)

# generates list of tuples as (Ticker:score_to_add) for a comment
def comment_score(comment):

    remove_links(comment)

    if check_all_capitalized(comment):
        return None

    clean_comment(comment)

    removed_symbol_present = check_removed(comment)

    # extract symbols
    symbols_present = extract_symbols(comment)
    # calulcate scores
    for ticker in symbols_present:
        score = 1 + comment.score * 0.05
        ticker.score = round(score, 2)
    return symbols_present


#TODO
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

# TODO
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

#TODO
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

# Removes most links from the comments using regex
def remove_links(comment):
    comment.body = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    comment.body = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    return

# TODO
def check_all_capitalized(comment):
    all_cap = False

    num_letters = len(comment.body)
    cap_only = re.sub(r'[^A-Z]+', '', comment.body)
    num_cap = len(cap_only)

    if num_letters > 0:
        if num_cap / num_letters > 0.2  or num_cap > 20:
            all_cap = True
    return all_cap


# TODO Add caching for these values
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

# TODO This is a touch unnecessary
def get_time():
    return datetime.datetime.now()

# Gets the number of hours since the script started running
def get_index():
    # Make sure the file 'Data/start' exists
    name = 'Data/start'
    fname = pathlib.Path(name)
    assert fname.exists(), f'File {name} does not exist!'

    # If so, use its timestamp as the starting timestamp
    start_time = datetime.datetime.fromtimestamp(fname.stat().st_mtime)
    current_time = datetime.datetime.now()
    dif = current_time - start_time

    # Calculate the number of hours since the start of the data gathering process
    total_hours = dif.total_seconds() / 3600
    if total_hours < 0:
        total_hours = 0

    # Return the total number of elapsed hours as the index
    return total_hours

#TODO
def wait_for_next_hour():
    minutes_until_next_hour = 60 - datetime.datetime.now().minute
    time.sleep(60 * minutes_until_next_hour)

