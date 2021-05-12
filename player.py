class Player:
    def __init__(self, fq, display, id_):
        self.fq = fq
        self.display = display
        self.id_ = id_

    def __str__(self):
        return f'{self.id_} - {self.display}'
