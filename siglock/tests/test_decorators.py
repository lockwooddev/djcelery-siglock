import mock
import hashlib
from django.core.cache import cache

from siglock.decorators import single_task


def test_single_task_no_arguments(add_mock):
    """ Tests cache key without any args or kwargs """

    def fn():
        pass

    # decorate & call
    single_task(60)(fn)()

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_with_args(add_mock):
    """ Tests cache key with args """

    def fn(*args):
        pass

    # decorate & call
    single_task(60)(fn)('1', 2, None, False)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_1_2_None_False', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_with_kwargs(add_mock):
    """ Tests cache key with kwargs """

    def fn(**kwargs):
        pass

    # decorate & call
    single_task(60)(fn)(a='1', b=2, c=None, d=False)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_a_1_b_2_c_None_d_False', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_with_args_and_kwargs(add_mock):
    """ Tests cache key with both args and kwargs """

    def fn(*args, **kwargs):
        pass

    # decorate & call
    single_task(60)(fn)(1, 2, a='b', b='c')

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_1_2_a_b_b_c', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_single_argument(add_mock):
    """ Tests cache key with single arg """

    def fn(arg):
        pass

    # decorate & call
    single_task(60)(fn)(1)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_arg_1', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_with_list_as_argument(add_mock):
    """ Tests cache key with list as argument """

    def fn(lst):
        pass

    # decorate & call
    single_task(60)(fn)([1, 2])

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_lst_[1,2]', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_with_float_as_argument(add_mock):
    """ Tests cache key with float as argument """

    def fn(f):
        pass

    # decorate & call
    single_task(60)(fn)(1.2345)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_f_1.2345', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_default_arguments(add_mock):
    """ Tests cache key with default arguments """

    def fn(a=False, b=None, *args):
        pass

    # decorate & call
    single_task(60)(fn)(1, 2, 3, 4)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_a_False_b_None_1_2_3_4', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_override_default_arguments(add_mock):
    """ Tests cache key with defaults which are overriden """

    def fn(a=False, b=None, **kwargs):
        pass

    # decorate & call
    single_task(60)(fn)(a=True, b=1, c=2)

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn_a_True_b_1_c_2', 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_ignore_arguments(add_mock):
    """ Tests task arguments are ignored and cache key generated from function name """

    def fn(lst):
        pass

    # decorate & call
    single_task(60, ignore_args=True)(fn)([1, 2, 3])

    assert add_mock.call_count == 1
    assert add_mock.call_args[0] == ('lock_fn', 'true', 60)


@mock.patch('django.core.cache.cache.delete')
def test_run_while_locked(cache_delete_mock):
    """ Test existing lock cache key set that prevents from running task again """

    def fn():
        pass

    cache.set('lock_fn', 'true', 60)
    single_task(60)(fn)()
    assert not cache_delete_mock.called


@mock.patch('django.core.cache.cache.add')
def test_single_task_digest_key_short(add_mock):
    """ Tests generated short cache key is md5 hashed """

    def fn(arg):
        pass

    # decorate & call
    single_task(60, digest=True)(fn)(1)

    m = hashlib.md5()
    m.update(b'lock_fn_arg_1')
    _hash = m.hexdigest()
    assert add_mock.call_args[0] == (_hash, 'true', 60)


@mock.patch('django.core.cache.cache.add')
def test_single_task_digest_key_long_arguments(add_mock):
    """ Tests generated long cache key is md5 hashed """

    def fn(lst):
        pass

    lst = [x for x in range(0, 300)]

    # decorate & call
    single_task(60, digest=True)(fn)(lst)

    expected_key = 'lock_fn_lst_{}'.format(str(lst).replace(' ', ''))

    m = hashlib.md5()
    m.update(expected_key.encode())
    _hash = m.hexdigest()
    assert add_mock.call_args[0] == (_hash, 'true', 60)
