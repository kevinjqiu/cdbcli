from contextlib import contextmanager


@contextmanager
def retry(max_retries, delay_ms, exception_type=Exception):  # pragma: no cover
    num_tries = 0

    while True:
        try:
            yield
        except exception_type:
            num_tries += 1
            if num_tries == max_retries:
                raise
        else:
            break
