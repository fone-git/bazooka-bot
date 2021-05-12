class GameSet:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.p1_score = 0
        self.p2_score = 0

    def __str__(self):
        return f'{self.p1} ({self.p1_score}) vs {self.p2} ({self.p2_score})'
