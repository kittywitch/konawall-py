import termcolor

"""
Print a key-value pair with a key and value coloured differently.

:param key: The key to print
:param value: The value to print
:param newline: Whether to print a newline after the value
:returns: None
"""
def kv_print(key: str, value: str, newline: bool = False) -> None:
    print(termcolor.colored(key, "cyan") + ": " + termcolor.colored(value, "white"), end="\n" if newline else " ")