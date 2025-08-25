import time
from functools import wraps

def log_time(func):
    """
    A decorator that prints the time a function takes to execute.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # Start the timer
        result = func(*args, **kwargs)   # Call the decorated function
        end_time = time.perf_counter()    # Stop the timer
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")
        return result
    return wrapper