from ftplib import FTP
import re
import os
import praw
import datetime
import time
import pathlib

from Ticker import *
from Comment_Info import *

debug = False

all_removed = set()

# Reads the sql database connection configuration information from the provided ini file
def get_sql_config():
    db = {}

    db['host'] = os.getenv('SQL_HOST')
    db['database'] = os.getenv('SQL_DB')
    db['user'] = os.getenv('SQL_USER')
    db['password'] = os.getenv('SQL_PASSWORD')

    return db


# TODO: This seems to not do much, but take a long time to do so
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


# TODO
def process_comment(comment, depth=0):
    yield Comment_Info(comment.body, depth, comment.score)
    for reply in comment.replies:
        yield from process_comment(reply, depth + 1)


# Generates list of tuples as (Ticker:score_to_add) for a comment
def comment_score(comment) -> set:
    if check_all_capitalized(comment):
        return None

    comment = remove_links(comment)

    comment = clean_comment(comment)

    # extract symbols
    symbols_present = extract_symbols(comment)
    removed_symbols = get_all_removed_symbols()

    # Then remove all symbols that aren't wanted
    symbols = symbols_present.difference(removed_symbols)

    # calulcate scores
    for ticker in symbols:
        score = 1 + comment.score * 0.05
        ticker.score = round(score, 2)

    return symbols


# TODO
def get_all_removed_symbols():
    # If the set is already loaded, don't bother reloading it
    if len(all_removed) == 0:
        symbol_reader = open('removed.txt', 'r')
        removed_symbols = symbol_reader.readlines()
        symbol_reader.close()

        for symbol in removed_symbols:
            all_removed.add(Ticker(symbol=symbol))

    return all_removed


# Gets all ticker symbols from a comment and returns them as a set of ticker objects
def extract_symbols(comment) -> set:
    comment.body = re.sub(r'[$]', '', comment.body)
    symbol_reader = open('symbols.txt', 'r')
    all_symbols = symbol_reader.readlines()
    symbol_reader.close()

    symbols_present = set()

    for symbol in all_symbols:
        symbol = symbol.rstrip()
        padded_symbol = ' ' + symbol + ' '
        if comment.body.find(padded_symbol) >= 0:
            symbols_present.add(Ticker(symbol=symbol))

    return symbols_present


# Removes most links from the comments using regex
def remove_links(comment):
    comment.body = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    comment.body = re.sub(r'[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', comment.body)
    return comment


# Cleans up the body of the comment before further processing
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

    return comment


# TODO
def check_all_capitalized(comment) -> bool:
    #return comment.body.isupper()
    all_cap = False

    num_letters = len(comment.body)
    cap_only = re.sub(r'[^A-Z]+', '', comment.body)
    num_cap = len(cap_only)

    if num_letters > 0:
        if num_cap / num_letters > 0.2  or num_cap > 20:
            all_cap = True
    return all_cap
