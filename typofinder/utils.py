import time
import datetime
from functools import wraps


def trim_trailing_slash(path: str) -> str:
    if path.endswith("/"):
        path = path[:-1]
    if len(path) <= 0:
        raise
    return path


def timeit(func):
    @wraps(func)
    def closure(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print("<%s> took %0.3fs." % (func.__name__, te - ts))
        return result

    return closure


def today_Ymd() -> str:
    return datetime.datetime.today().strftime("%Y%m%d")
