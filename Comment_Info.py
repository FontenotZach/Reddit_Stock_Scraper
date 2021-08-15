class Comment_Info:
    body = ''
    user = ''
    score = 0
    depth = 0

    def __init__(self, body, score, depth):
        self.body = body
        self.user = ''
        self.score = score
        self.depth = depth
