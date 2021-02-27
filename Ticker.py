class Ticker:

    symbol = ''
    score = 0
    price = 0
    trending_score = 0

    def __init__(self, symbol):
        self.symbol = symbol

    def is_same_symbol(self, t):
        if self.symbol == t.symbol:
            return True
        return False
