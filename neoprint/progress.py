import typing as tp
from . import text_object as to
from .config import config
from .console import console
from .debugger import debugger
from .format import get_head_parts
from .frame_info import FrameInfo


class Progress:
    def __init__(
        self,
        total: tp.Optional[int] = None,
        indicator_style: tp.Literal[
            'counter', 'digital', 'decimal', 'none'
        ] = 'counter',
        color: tp.Literal['blue', 'green', 'yellow', 'red'] = 'red',
    ) -> None:
        """
        params:
            total:
                you can pass it now or later by `total` property.
                the total value can be modified multiple times until
                `update()` is called.
        """
        # for modern terminal, we use same char for filled and unfilled but
        # different colors. for legacy terminal or debug mode, we use different
        # chars for filled and unfilled.
        # TODO: detect legacy terminal.
        self.filled_char = '─'
        self.unfilled_char = '─'
        self._debug_filled_char = '█'
        self._debug_unfilled_char = '░'

        self.index = 0
        self.indicator_style = indicator_style
        self._accent_color = color
        self._bar_length = 40
        self._head_parts = (
            tuple(get_head_parts(FrameInfo.parent_place()))
            if config.show_source
            else ()
        )
        self._head_length = sum(map(len, self._head_parts))
        self._is_spinner = False
        self._total: tp.Optional[int] = total
        self._type_determined = False

    def __enter__(self) -> 'Progress':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    @property
    def total(self) -> tp.Optional[int]:
        return self._total

    @total.setter
    def total(self, value: int) -> None:
        if self._type_determined:
            raise ValueError(
                'cannot set `total` after `Progress.update()` has been called '
                'because the progress type has been determined.'
            )
        self._total = value

    def update(self, item: tp.Optional[tp.Union[str, to.Text]] = None):
        if not self._type_determined:
            self._type_determined = True
            self._is_spinner = self._total is None
            if self._is_spinner:
                raise NotImplementedError

        self.index += 1
        index = self.index
        total = tp.cast(int, self._total)
        body_parts = []
        if debugger.enabled:
            filled_char, unfilled_char = (
                self._debug_filled_char,
                self._debug_unfilled_char,
            )
            end = '\n'
        else:
            filled_char, unfilled_char = self.filled_char, self.unfilled_char
            end = '\033[K\r'

        prog_value = min((1, index / total))  # 0.00 ~ 1.00
        filled_len = round(self._bar_length * prog_value)
        unfilled_len = self._bar_length - filled_len
        if filled_len:
            body_parts.append(
                to.Text(filled_char * filled_len, self._accent_color)
            )
        if unfilled_len:
            body_parts.append(
                to.Text(unfilled_char * unfilled_len, 'default', 'dim')
            )

        if self.indicator_style != 'none':
            body_parts.append(to.Space())
            # indicator example:
            #   counter    digital  decimal
            #   ---------  -------  ---------
            #   [  1/100]  (  1%)   (  1.00%)
            #   [ 10/100]  ( 10%)   ( 10.00%)
            #   [100/100]  (100%)   (100.00%)
            body_parts.append(
                to.Text(
                    '[{:>{}}/{}]'.format(index, len(str(total)), total)
                    if self.indicator_style == 'counter'
                    else '({:>{}.{}%})'.format(
                        prog_value,
                        4 if self.indicator_style == 'decimal' else 7,
                        0 if self.indicator_style == 'digital' else 2,
                    ),
                    self._accent_color,
                )
            )

        left_space = (
            console.width - self._head_length - sum(map(len, body_parts))
        )
        assert left_space >= 0
        if item and left_space > 3:
            body_parts.append(to.Space())
            left_space -= 1
            body_parts.append(
                to.Text(item[:left_space]) if isinstance(item, str) else 
                to.Text(item._origin[:left_space], item.color, item.style)
            )

        line = ''.join(
            x.render(color_code_scheme='ansi') for x in self._head_parts
        ) + ''.join(x.render(color_code_scheme='ansi') for x in body_parts)
        console.print(line, end=end, flush=True)

    def close(self) -> None:
        if not debugger.enabled:
            console.print('', flush=True)
        self.reset()

    def reset(self) -> None:
        self.index = 0
        self._is_spinner = False
        self._total = None
        self._type_determined = False


class ProgressItem:
    def __init__(self, data, label: str = ''):
        self.data = data
        self.label = label or str(data)


class Spinner(Progress): ...


def progress(
    obj: tp.Iterable, total: tp.Optional[int] = None, **kwargs
) -> tp.Iterator:
    if total is None:
        if isinstance(obj, (dict, frozenset, list, tuple, set)):
            total = len(obj)

    with Progress(total=total, **kwargs) as prog:
        for item in obj:
            if isinstance(item, ProgressItem):
                prog.update(item.label)
                yield item.data
            else:
                prog.update()
                yield item


def spinner(obj: tp.Iterable, **kwargs): ...
