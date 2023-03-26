
import types

from itertools import islice


def batch_iter(iterable, batch_size=1):
    if isinstance(iterable, types.GeneratorType):
        while True:
            batch = list(islice(iterable, batch_size))
            if not batch:
                break
            yield batch
    else:
        length = len(iterable)
        for idx in range(0, length, batch_size):
            yield iterable[idx:min(idx + batch_size, length)]
