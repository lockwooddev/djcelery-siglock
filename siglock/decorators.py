import copy
import logging
from collections import OrderedDict
from functools import wraps
from inspect import signature, Parameter

from django.core.cache import cache


logger = logging.getLogger(__name__)


def _join(*args):
    return '_'.join(args)


def get_signature(fn, args, kwargs):
    _args = list(copy.deepcopy(args))
    _kwargs = copy.deepcopy(kwargs)

    lock_id = 'lock_{0}'.format(fn.__name__)

    keyword_args = OrderedDict()
    sig = signature(fn)

    for key in sig.parameters:
        if key is not 'args' and key is not 'kwargs':
            value = sig.parameters[key].default

            # map first value of args to the required keyword argument
            if value == Parameter.empty:
                value = _args.pop(0)

            # if keyword arg is overwritten by **kwargs, then use new and delete old
            if key in _kwargs:
                value = _kwargs[key]
                del _kwargs[key]

            keyword_args[key] = value

    if keyword_args:
        keywords_part = _join(*[_join(k, str(keyword_args[k])) for k in keyword_args])
        lock_id = _join(lock_id, keywords_part)

    # join _args and append to cache key
    if _args:
        args_part = _join(*[str(x) for x in _args])
        lock_id = _join(lock_id, args_part)

    # join _kwargs and append to cache key
    if _kwargs:
        # sort kwarg keys first for same result always
        sorted_kwargs = sorted(_kwargs)
        kwargs_part = _join(*[_join(k, str(_kwargs[k])) for k in sorted_kwargs])
        lock_id = _join(lock_id, kwargs_part)

    # remove whitespace from cache key
    lock_id = lock_id.replace(' ', '')

    return lock_id


def single_task(timeout, ignore_args=False):
    """
    Decorator locking a celery task that should only run once.

    | ``Example:``
    ::

        @single_task(timeout=60 * 5)
        def task():
            pass
    """

    def _dec(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not ignore_args:
                lock_id = get_signature(fn, args, kwargs)
            else:
                lock_id = 'lock_{0}'.format(fn.__name__)

            # adds key to cache, but not overriding
            acquire_lock = lambda: cache.add(lock_id, 'true', timeout)
            release_lock = lambda: cache.delete(lock_id)

            if acquire_lock():
                logger.debug('Task locked: {0} set for {1} seconds'.format(lock_id, timeout))
                try:
                    fn(*args, **kwargs)
                finally:
                    release_lock()
                    logger.debug('Task reset lock: {0}'.format(lock_id))

        return wrapper
    return _dec
