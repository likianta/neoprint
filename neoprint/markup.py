import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple


class MarkType(Enum):
    COLOR = auto()
    DIVIDER = auto()
    EXPAND = auto()
    FLUSH = auto()
    INDEX = auto()
    PARENT = auto()
    RICH = auto()
    SHORT = auto()
    TIMER = auto()
    VERBOSITY = auto()


@dataclass
class ParsedMarks:
    color: Optional[int] = None
    divider: Optional[int] = None
    expand: Optional[int] = None
    flush: Optional[int] = None
    index: Optional[int] = None
    parent: Optional[int] = None
    rich: Optional[int] = None
    short: Optional[int] = None
    timer: Optional[int] = None
    verbosity: Optional[int] = None


class MarkupParser:
    _mark_pattern = re.compile(r'^:(?:[cdfilprstv][0-9]?)+$')
    _mark_token_pattern = re.compile(r'([cdfilprstv])([0-9]?)')

    _defaults: Dict[str, int] = {
        'c': 0,
        'd': 0,
        'f': 0,
        'i': 2,
        'l': 0,
        'p': 1,
        'r': 0,
        's': 0,
        't': 1,
        'v': 0,
    }

    _key_to_attr: Dict[str, str] = {
        'c': 'color',
        'd': 'divider',
        'f': 'flush',
        'i': 'index',
        'l': 'expand',
        'p': 'parent',
        'r': 'rich',
        's': 'short',
        't': 'timer',
        'v': 'verbosity',
    }

    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern.match(text))

    def parse(self, markup: str) -> ParsedMarks:
        marks = ParsedMarks()
        for match in self._mark_token_pattern.findall(markup) or []:
            key = match[0]
            value = int(match[1]) if match[1] else self._defaults.get(key, 0)
            attr = self._key_to_attr.get(key, key)
            setattr(marks, attr, value)
        return marks

    def extract_from_args(
        self, args: Tuple[Any, ...]
    ) -> Tuple[Tuple[Any, ...], int, ParsedMarks]:
        markup_pos = 0
        markup = ''
        raw_args = args

        if (
            len(args) > 0
            and isinstance(args[0], str)
            and args[0].startswith(':')
            and self.is_valid_markup(args[0])
        ):
            markup_pos = 1
            markup = args[0]
            raw_args = args[1:]
        elif (
            len(args) > 1
            and isinstance(args[-1], str)
            and args[-1].startswith(':')
            and self.is_valid_markup(args[-1])
        ):
            markup_pos = -1
            markup = args[-1]
            raw_args = args[:-1]
        else:
            markup_pos = 0
            raw_args = args

        parsed = self.parse(markup) if markup else ParsedMarks()
        return raw_args, markup_pos, parsed


parser = MarkupParser()
