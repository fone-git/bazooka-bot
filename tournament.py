from player import Player
from round import Round


class Tournament:
    def __init__(self):
        self.next_id = 0
        self.is_reg_open = True
        self.players = []

        # Stores the rounds
        # NB: Used for display purposes only during registration
        self.rounds_ = None

    def register(self, user_fq, user_display):
        if not self.is_reg_open:
            raise Exception(f'Registration is closed')

        if user_fq in self:
            raise Exception(f'{user_display} already exists')
        self.rounds_ = None
        player = Player(user_fq, user_display, self.get_id())
        self.players.append(player)
        return player.id_

    def __contains__(self, fq):
        for player in self.players:
            if player.fq == fq:
                return True
        return False

    def get_id(self):
        self.next_id += 1
        return self.next_id

    def close_registration(self):
        # TODO Fill out rest of rounds
        pass

    @property
    def rounds(self):
        if self.rounds_ is None:
            round_ = Round()
            self.rounds_ = [round_]
            p1 = None
            for player in self.players:
                if p1 is None:
                    p1 = player
                else:
                    round_.add(p1, player)
                    p1 = None

            # If there were an odd number of players and one is left over
            # put them into a game by themselves (auto win)
            if p1 is not None:
                round_.add(p1)

        return self.rounds_

    def __str__(self):
        result = ""
        for i, round_ in enumerate(self.rounds):
            result += f'--- Round {i} ---\n{round_}\n'
        return result
