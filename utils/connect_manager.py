import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Timer
from typing import Optional

from opylib.log import log, log_exception

from conf import Conf, DBKeys
from utils.db_cache import DBCache
from utils.timer_funcs import set_timeout

REF_DATE_IN_PAST = datetime.fromtimestamp(0)


@dataclass
class ConnFailInfo:
    last_time: datetime
    fail_count: int
    err_msg: str

    def __str__(self):
        last_time = None if self.last_time == REF_DATE_IN_PAST else \
            self.last_time
        return (
            f'Last Fail Date/Time: {last_time}\n'
            f'Fail Count: {self.fail_count}\n'
            f'Last Error Message: "{self.err_msg}"'
        )


class ConnectManager:
    def __init__(self, func: callable, db: DBCache):
        self.func: callable = func
        self.db: DBCache = db
        self.retry_timer: Optional[Timer] = None
        self._next_attempt_time: Optional[datetime] = None
        self.connected = False

    @staticmethod
    def num_fails_to_timedelta(num_fails) -> timedelta:
        assert num_fails >= 0
        result = math.ceil(
            Conf.FAILED_CONNECT_INITIAL_DELAY.total_seconds() / 60)

        # 0 and 1 both have a delay of 'Initial Delay'
        for i in range(1, num_fails):
            result *= 2  # Double delay each fail
        return timedelta(minutes=result)

    @property
    def next_attempt_time(self) -> datetime:
        if self._next_attempt_time is None:
            last_fail = self.get_last_conn_fail_info(self.db)
            self._next_attempt_time = \
                last_fail.last_time + self.num_fails_to_timedelta(
                    last_fail.fail_count)
        return self._next_attempt_time

    def inc_next_attempt_time(self, fail_info: ConnFailInfo):
        self._next_attempt_time = (
                fail_info.last_time +
                self.num_fails_to_timedelta(fail_info.fail_count))

    @classmethod
    def get_last_conn_success(cls, db: DBCache) -> Optional[datetime]:
        return db.get(DBKeys.CM_LAST_CONN_SUCCESS_DT, should_yaml=True)

    @classmethod
    def set_last_conn_success(cls, value: datetime, db: DBCache):
        db[DBKeys.CM_LAST_CONN_SUCCESS_DT, True] = value

    @classmethod
    def get_last_conn_fail_info(cls, db: DBCache) -> ConnFailInfo:
        if db.get(DBKeys.CM_LAST_CONN_FAIL_INFO, should_yaml=True) is None:
            cls.init_last_conn_fail_info(db)
        return db[DBKeys.CM_LAST_CONN_FAIL_INFO, True]

    @classmethod
    def set_last_conn_fail_info(cls, value: ConnFailInfo, db: DBCache):
        db[DBKeys.CM_LAST_CONN_FAIL_INFO, True] = value

    def get_time_before_connect_allowed(self) -> Optional[timedelta]:
        """
        Checks the amount of time left before a connection is allowed. If the
        time is greater than 0 seconds then that value is returned otherwise
        None is returned.
        :return: Time before connection allowed or None if connection is
            allowed now
        """
        time_left = self.next_attempt_time - datetime.now()
        return None if time_left.total_seconds() <= 0 else time_left

    def try_connect(self):
        time_before_conn = self.get_time_before_connect_allowed()
        if time_before_conn is None:
            try:
                log('Going to attempt to connect')
                self.func()
            except Exception as e:
                log_exception(e)

                # Get last fail info
                last_info = self.get_last_conn_fail_info(self.db)

                # Register Failed attempt
                new_fail_info = ConnFailInfo(
                    datetime.now(), last_info.fail_count + 1, str(e))
                self.set_last_conn_fail_info(new_fail_info, self.db)
                self.inc_next_attempt_time(new_fail_info)
                self.request_retry_attempt()
        else:
            if self.retry_timer is None or not self.retry_timer.is_alive():
                # Second part of if condition not tested because the first
                # should only happen on startup while still on cool down and the
                # later should not happen because nothing should call this
                # function while a timer has already been created until that
                # timer fired, at which time it should retry not come here
                self.request_retry_attempt()
            else:
                # Not tested, code should NOT reach here because calls are
                # not made to try_connect except once in main and by timer
                log('Active retry timer already in progress')

    @classmethod
    def status(cls, db: DBCache):
        last_fail_info = cls.get_last_conn_fail_info(db)
        return (
            f'Server Time Now: {datetime.now()}\n'
            f'Last successful connection: {cls.get_last_conn_success(db)}\n'
            f'{last_fail_info}\n'
        )

    @classmethod
    def reset_fail_count(cls, db: DBCache):
        last_fail = cls.get_last_conn_fail_info(db)
        cls.set_last_conn_fail_info(
            ConnFailInfo(last_fail.last_time, 0, ''), db)

    def status_as_html(self):
        if self.connected:
            return ''
        now_ = datetime.now()
        msg = (
            f'Connection Status: Disconnected\n'
            f'Next Attempt time: {self.next_attempt_time}\n'
            f'Time Left: {self.next_attempt_time - now_}\n'
            f'{self.status(self.db)}'
        )
        return msg.replace('\n', '<br />')

    def request_retry_attempt(self):
        sec_to_next_attempt = \
            (self.next_attempt_time - datetime.now()).total_seconds()
        assert sec_to_next_attempt > 0
        self.retry_timer = set_timeout(sec_to_next_attempt, self.try_connect)
        log(f'Set retry timer for {sec_to_next_attempt / 60} minutes')

    @classmethod
    def init_last_conn_fail_info(cls, db: DBCache):
        cls.set_last_conn_fail_info(ConnFailInfo(REF_DATE_IN_PAST, 0, ''), db)
