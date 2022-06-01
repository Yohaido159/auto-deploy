from pprint import pprint
from functools import wraps


def event_logger(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f'\nCalled {fn.__name__} with ')
        print(f'args:')
        for arg in args:
            pprint(arg)
        print(f'kwargs:')
        for k, v in kwargs.items():
            pprint(f'{k}={v}')

        print(f'-----------------\n')

        return fn(*args, **kwargs)

    return wrapper
