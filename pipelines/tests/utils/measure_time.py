import datetime
import time


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed = end_time - start_time
        return result, elapsed

    return wrapper


class Timer:
    def __init__(self):
        self.process_terminated = False

    def __enter__(self):
        self.start = datetime.datetime.now()
        return self

    @property
    def start_time(self):
        return self.start

    @property
    def spent_time(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.start_time

    @property
    def seconds_from_start(self) -> float:
        return self.spent_time.total_seconds()

    def __exit__(self, *args):
        return self.process_terminated
