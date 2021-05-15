class Player:
    def __init__(self, id_, display, disp_id):
        self.id = id_
        self.display = display
        self.disp_id = disp_id

    def __str__(self):
        return f'{self.disp_id} - {self.display}'
