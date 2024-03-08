from sys import stderr, stdout
from typing import IO


def eprint(msg: str, *args, file: IO = stderr, **kwargs):
    """Prints an error message to the console formatted as `ERROR: <message>`.

    :param msg: The message to print, will be formatted with `*args`.
    :param args: An iterable to format `msg` with.
    :param file: The file to print to.
    :param kwargs: Additional keyword arguments to the regular `print()`-function."""
    msg = msg % args
    print(f"ERROR: {msg}", file=file, **kwargs)


def iprint(msg: str, *args, file: IO = stdout, **kwargs):
    """Prints an info message to the console formatted as `INFO: <message>`.

    :param msg: The message to print, will be formatted with `*args`.
    :param args: An iterable to format `msg` with.
    :param file: The file to print to.
    :param kwargs: Additional keyword arguments to the regular `print()`-function."""
    msg = msg % args
    print(f"INFO: {msg}", file=file, **kwargs)
