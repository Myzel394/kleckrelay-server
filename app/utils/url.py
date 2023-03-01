__all__ = [
    "Components",
]

from collections import namedtuple

Components = namedtuple(
    typename='Components',
    field_names=['scheme', 'netloc', 'url', 'path', 'query', 'fragment'],
)
