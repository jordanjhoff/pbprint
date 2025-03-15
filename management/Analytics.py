import functools
import json
import os
import threading
from datetime import datetime

analytics_file = "analytics.json"
analytics_lock = threading.Lock()

if os.path.exists(analytics_file):
    with open(analytics_file, "r") as f:
        analytics = json.load(f)
else:
    analytics = {}


def log_event(func_name, arg_value=None):
    """Logs an event count based on function name and argument value."""
    with analytics_lock:
        if func_name not in analytics:
            analytics[func_name] = {"count": 0}

        analytics[func_name]["count"] += 1

        #This allows simple additional logging of a given argument (THIS IS A BAD WAY TO DO THIS LOLOLOL)
        if arg_value is not None:
            if "args" not in analytics[func_name]:
                analytics[func_name]["args"] = {}

            analytics[func_name]["args"].setdefault(arg_value, {"count": 0})
            analytics[func_name]["args"][arg_value]["count"] += 1

        with open(analytics_file, "w") as file:
            json.dump(analytics, file, indent=4)

def log_function_call(arg_name: str):
    """
    Decorator that logs when a function is called, using the specified argument's value as the key.
    The argument that it logs should be a string.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_args = func.__code__.co_varnames[:func.__code__.co_argcount]

            if arg_name in func_args:
                arg_index = func_args.index(arg_name)
                if arg_index < len(args):
                    arg_value = args[arg_index]
                elif arg_name in kwargs:
                    arg_value = kwargs[arg_name]
                else:
                    return func(*args, **kwargs)

                log_event(func.__name__, arg_value)

            return func(*args, **kwargs)

        return wrapper

    return decorator