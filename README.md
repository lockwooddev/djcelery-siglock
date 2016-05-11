# djcelery-siglock

Djcelery-siglock is Celery task decorator to ensure that a task is only executed one at a time.

## What's unique about it?

Take a look first at the
[task lock decorator](http://docs.celeryproject.org/en/latest/tutorials/task-cookbook.html#ensuring-a-task-is-only-executed-one-at-a-time)
from the official Celery documentation.

What's different in this project, is the unique signature it tries to create based on the arguments used in executing the task function.
The signature is used as a cache key for locking the task.


## Installing & running tests

    make devinstall
    make tests


## Usage examples

### Importing

```python
from siglock import single_task
```

### Decorating task functions

```python
@task
@single_task(60 * 60)
def task1(obj_pk):
    pass

task1.delay(1)
```

The decorator argument `60 * 60` sets the cachekey timeout to one hour (in seconds).
The cache key generated will be `lock_task1_obj_pk_1`.

```python
@task
@single_task(60 * 60)
def task2():
    pass

task2.delay()
```
The cache key generated will be `lock_task2`.


```python
@task
@single_task(60 * 60)
def task3(*args, **kwargs):
    pass

task3.delay(1, a=2)
```
The cache key generated will be `lock_task3_1_a_2`.


## Beware

The cache key generator by the decorator expects the contents of arguments to be ordered.
Passing unordered list or dictionaries can create non-unique cache keys.
In this cache you should consider blocking the task as a whole until finished processing.

Here is an example:

```python
@task
@single_task(60 * 60, ignore_args=True)
def task4(lst):
    pass

task4.delay([1,2,3])
```
The cache key generated will be `lock_task4`.


## Hash cache key

If your cache key gets too long, you can also md5 hash your cache key.

```python
@task
@single_task(60 * 60, digest=True)
def task4(arg):
    pass

task4.delay(1)
```

The cache key generated will be a md5 hexdigest.
