from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from .parsers.base import BaseParser


class ParserRegistry:
    _parsers: Dict[str, Type[BaseParser]] = {}

    @classmethod
    def register(cls, name: str):
        def decorator(parser_cls: Type[BaseParser]):
            cls._parsers[name.lower()] = parser_cls
            return parser_cls
        return decorator

    @classmethod
    def get(cls, name: str) -> Type[BaseParser]:
        key = name.lower()
        if key not in cls._parsers:
            raise ValueError(f"No parser registered for '{name}'. Available: {list(cls._parsers)}")
        return cls._parsers[key]

    @classmethod
    def available(cls):
        return list(cls._parsers.keys())
