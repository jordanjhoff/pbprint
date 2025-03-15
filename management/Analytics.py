import functools


def log_function_call(func):
    """Decorator that logs when a function is called."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper