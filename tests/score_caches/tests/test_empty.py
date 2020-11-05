from pytest import raises

from ores.score_caches.empty import Empty


def test_empty():
    """
    Create an empty empty.

    Args:
    """

    empty = Empty()
    context = empty.context("foo", "bar", version="nope")
    context.store(1, "foo")


def test_key_error():
    """
    Display a test key.

    Args:
    """
    with raises(KeyError):
        empty = Empty()
        context = empty.context("foo", "bar", version="nope")
        context.store(1, "foo")
        context.lookup(1)
