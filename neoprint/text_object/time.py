from time import localtime
from time import strftime

from .base import T
from .base import TextObject
from ..render import render


class TimeDuration(TextObject):
    _color_d: T.Color
    _color_e: T.Color
    _color_s: T.Color
    _short_form: bool
    _time_d: str
    _time_e: str
    _time_s: str
    _too_short: bool

    def __init__(
        self, start: float, end: float, short_form: bool = False
    ) -> None:
        duration = end - start
        self._color_s = 'green'
        self._color_e = (
            'green'
            if duration < 1.000
            else 'yellow'
            if duration < 5.000
            else 'red'
        )
        self._color_d = self._color_e
        self._too_short = int(start) == int(end)
        self._time_s = pretty_time(start)
        self._time_e = pretty_time(end)
        self._time_d = pretty_duration(duration)
        self._short_form = short_form
        self.editable = False

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        if self._short_form:
            return render(
                ('[', self._color_e, 'dim' if self._too_short else ''),
                (self._time_e, self._color_e, 'dim' if self._too_short else ''),
                (
                    '{:>8}'.format('({})'.format(self._time_d)),
                    self._color_d,
                    'dim' if self._too_short else '',
                ),
                (']', self._color_e, 'dim' if self._too_short else ''),
                color_code_scheme=color_code_scheme,
            )
        else:
            return render(
                ('[', 'default', ''),
                (self._time_s, self._color_s, ''),
                (' -> ', 'default', 'dim'),
                (self._time_e, self._color_e, 'dim' if self._too_short else ''),
                (
                    '{:>8}'.format('({})'.format(self._time_d)),
                    self._color_d,
                    'dim' if self._too_short else '',
                ),
                (']', 'default', ''),
                color_code_scheme=color_code_scheme,
            )


class TimeStamp(TextObject):
    def __init__(self, current_time: float) -> None:
        self._timestamp = '[{}]'.format(pretty_time(current_time))

    def render(self, color_code_scheme: T.ColorCodeScheme = 'plain') -> str:
        return render(
            (self._timestamp, self.color, self.style),
            color_code_scheme=color_code_scheme,
        )


# def pretty_duration(t: float, sep: str = '') -> str:
#     if t >= 3600:
#         return sep.join(
#             (
#                 '{:.0f}h'.format(t // 3600),
#                 '{:.0f}m'.format(t % 3600 // 60),
#                 '{:.0f}s'.format(t % 60),
#             )
#         )
#     elif t >= 60:
#         # return '{:.1f}min'.format(t / 60)
#         return sep.join(('{:.0f}m'.format(t // 60), '{:.0f}s'.format(t % 60)))
#     elif t >= 1:
#         return '{:.1f}s'.format(t)
#     elif t == 0:
#         return '0s'
#     else:
#         for unit in ('ms', 'us', 'ns'):
#             t *= 1000
#             if t >= 1:
#                 return f'{round(t)}{unit}'
#         else:
#             raise Exception('time too short', t)


def pretty_duration(duration: float) -> str:
    return (
        '{:.0f}ms'.format(duration * 1000)
        if duration < 1.000
        else '{:.1f}s'.format(duration)
    )


def pretty_time(time: float) -> str:
    return strftime('%H:%M:%S', localtime(time))
