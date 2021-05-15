class Player:
    def __init__(self, fq, display, disp_id):
        self.fq = fq
        self.display = display
        self.disp_id = disp_id

    def __str__(self):
        return f'{self.disp_id} - {self.display}'
