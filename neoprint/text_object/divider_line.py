import typing as t

from .base import T
from .base import TextObject
from .base import TextObjectGroup
from .invisible import Space
from .text import Text
from ..console import console


class DividerLine(TextObjectGroup):
    def __init__(
        self,
        body_parts: t.Sequence[TextObject],
        non_body_parts: t.Sequence[TextObject],
        bold: bool = False,
    ) -> None:
        super().__init__()
        self._div_char = '█' if bold else '─'

        body_space = console.width - sum(map(len, non_body_parts))
        if body_parts:
            spare_space = body_space - sum(map(len, body_parts)) - 2
            #   `-2` for space around `body_parts`.
            assert spare_space >= 2
            #   spare_space should be at least 2 -- one for the left part of
            #   divchar, another for the right.
            left_part_space = spare_space // 2
            right_part_space = (
                left_part_space if spare_space % 2 == 0 else left_part_space + 1
            )
            self._objs.extend(
                (
                    Text(self._div_char * left_part_space),
                    Space(),
                    *body_parts,
                    Space(),
                    Text(self._div_char * right_part_space),
                )
            )
        else:
            assert body_space > 0
            self._objs.append(Text(self._div_char * body_space, style='dim'))

        self._full_dimmed_line = not body_parts

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        if self._full_dimmed_line:
            assert len(self._objs) == 1
            self._objs[0].style = 'dim'  # make sure the line is dimmed.
            return self._objs[0].render(color_code_scheme=color_code_scheme)
        else:
            return super().render(color_code_scheme=color_code_scheme)
