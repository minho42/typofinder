import time
import datetime
from functools import wraps


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

