from time import time_ns
from uuid import uuid4


def toke_gen_uniqe():
    return f"{time_ns()}{str(uuid4()).replace('-', '')}"
