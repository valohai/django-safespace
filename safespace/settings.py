from functools import lru_cache
from typing import Set, Type

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULT_EXCEPTION_CLASSES = [
    'django.core.exceptions.ValidationError',
    'safespace.excs.Problem',
]


@lru_cache()
def get_exception_classes() -> Set[Type[Exception]]:
    """
    Get the set of exceptions the middleware should handle from the settings.
    """
    class_names = getattr(
        settings, 'SAFESPACE_EXCEPTION_CLASSES', DEFAULT_EXCEPTION_CLASSES
    )
    classes = [import_string(class_name) for class_name in class_names]
    return set(classes)


def _uncache_settings(sender, **kwargs) -> None:  # type: ignore[no-untyped-def]  # pragma: no cover  # noqa:E501
    get_exception_classes.cache_clear()


setting_changed.connect(_uncache_settings)
