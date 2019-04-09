from functools import lru_cache

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

DEFAULT_EXCEPTION_CLASSES = [
    'django.core.exceptions.ValidationError',
    'safespace.excs.Problem',
]


@lru_cache()
def get_exception_classes():
    """
    Get the set of exceptions the middleware should handle from the settings.

    :type: set[class]
    """
    class_names = getattr(
        settings, 'SAFESPACE_EXCEPTION_CLASSES', DEFAULT_EXCEPTION_CLASSES
    )
    classes = [import_string(class_name) for class_name in class_names]
    return set(classes)


def _uncache_settings(sender, **kwargs):  # pragma: no cover
    get_exception_classes.cache_clear()


setting_changed.connect(_uncache_settings)
