class Ticker:

    symbol = ''
    score = 0
    price = 0
    trending_score = 0

    def __init__(self, symbol, score=0):
        self.symbol = symbol
        self.score = score

    def is_same_symbol(self, t):
        return self.symbol == t.symbol
