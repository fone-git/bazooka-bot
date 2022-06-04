from threading import Timer
from typing import Optional


class ConnectManager:
    def __init__(self, func: callable):
        self.func: callable = func
        self.timer: Optional[Timer] = None

    def check_allowed_run(self) -> bool:
        """
        Checks if connecting is allowed, if not it does the appropriate log msg
        :return: True if allowed to connect otherwise False
        """
        return False

    def try_connect(self):
        self.func()
        return
