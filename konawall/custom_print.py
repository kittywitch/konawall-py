import logging
import termcolor

"""
Print a key-value pair with a key and value.

:param key: The key to print
:param value: The value to print
:param level: The logging level to print at
:returns: None
"""
def kv_print(key: str, value: str, level: str = "INFO") -> None:
    logger = getattr(logging, level.lower())
    logger(f"{key}: {value}")