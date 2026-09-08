import re
import typing as tp

from .config import config
from .frame import FrameInfo
from .scope import counter
from .scope import scope_mgr
from .scope import timer


class T:
    Marks = tp.TypedDict(
        'Marks',
        {
            'd': int,  # divider line
            'e': int,  # exception trace back
            'f': int,  # flush
            'i': int,  # index
            'l': int,  # long / loose / expanded (multiple lines)
            'n': int,  # show varnames
            'p': int,  # parent layer
            'r': int,  # rich style
            's': int,  # short / simple / single line
            't': int,  # timer / timestamp
            'v': int,  # verbosity / log level
        },
        total=False,
    )
    Markup = str


class Mark:
    """
    turn digital values into descriptive values.

    usage: see `./format.py:format_list`.

    description:
        (the asterisk symbol on the left means default entry)
            d0  do not show divider line
        *   d1  default divider line
            d2  bold divider line
            e0  show error in plain format
            e1  show error with red color
        *   e2  show exception traceback panel
            e3  show exception traceback with locals
            e4  enter pdb                                      *(not supported)*
            f0  no flush
        *   f1  flush
            f2  flush cutoff
            f3  flush eddy                  *(not a good option, maybe removed)*
            i0  reset index
        *   i1  line-level index
            i2  scoped index
            i3  global index
            l0  no expand object
        *   l1  long / loose / expanded (multiple lines) format
            l2  expand object in tailored format
            n0  do not show varnames
        *   n1  show varnames
            n2  show varnames and expressions                  *(not supported)*
            p0  self layer
        *   p1  parent layer
            p2  grandparent layer                       *(be careful using p2+)*
            p3  great-grandparent layer
            p4  and so on...
            r0  no rich style
        *   r1  rich style
            r2  special rich object (rich.table.Table, rich.panel.Panel, etc.)
            s0  plain text
        *   s1  short / simple / single line
            s2  builtin print
            t0  reset timer
            t1  time stamp
        *   t2  time since last timer (relative)
            t3  time since last reset (absolute)
        *   v0  debug (gray)
            v1  negative info (magenta)
            v2  positive info (blue)
            v3  weak success (green dim)
            v4  success (green)
            v5  weak warning (yellow dim)
            v6  warning (yellow)
            v7  weak error / failure (red dim)
            v8  error / failure (red)
            v9  critical, fatal error (white on red)           *(not supported)*

        trick to remember `v*`:
            v2/4/6/8 are accent colors.
            v1/3/5/7 are dimmed colors.
    """

    NO_DIVIDER_LINE = 0  # :d0
    THIN_DIVIDER_LINE = 1  # :d1
    THICK_DIVIDER_LINE = 2  # :d2

    NO_ERROR_STYLE = 0  # :e0
    SIMPLE_ERROR_LINE = 1  # :e1
    TRACEBACK_EXCEPTION = 2  # :e2
    TRACEBACK_EXCEPTION_WITH_LOCALS = 3  # :e3

    NO_FLUSH = 0  # :f0
    FLUSH = 1  # :f1
    FLUSH_CUTOFF = 2  # :f2
    FLUSH_EDDY = 3  # :f3

    NO_INDEX_STUFF = -1
    RESET_INDEX = 0  # :i0
    LINE_LEVEL_INDEX = 1  # :i1
    SCOPED_INDEX = 2  # :i2
    GLOBAL_INDEX = 3  # :i3

    NO_EXPAND_FORMAT = 0  # :l0
    EXPAND_FORMAT = 1  # :l1
    SPECIAL_EXPAND_FORMAT = 2  # :l2

    NO_VARNAMES = 0  # :n0
    SHOW_VARNAMES = 1  # :n1

    SELF_LAYER = 0  # :p0
    PARENT_LAYER = 1  # :p1
    GRAND_PARENT_LAYER = 2  # :p2
    GREAT_GRAND_PARENT_LAYER = 3  # :p3
    ...  # :p4+

    NO_RICH_FORMAT = 0  # :r0
    RICH_FORMAT = 1  # :r1
    RICH_OBJECT = 2  # :r2

    NO_SHORT_SCHEME = 0  # :s0
    SHORT = 1  # :s1
    BUILTIN_PRINT = 2  # :s2

    NO_TIMER_STUFF = -1
    RESET_TIMER = 0  # :t0
    TIMESTAMP = 1  # :t1
    TIME_SINCE_LAST_TIME = 2  # :t2
    TIME_SINCE_START_TIME = 3  # :t3

    DEBUG = 0  # :v0
    NEGATIVE_INFO = 1  # :v1
    POSITIVE_INFO = 2  # :v2
    WEAK_SUCCESS = 3  # :v3
    SUCCESS = 4  # :v4
    WEAK_WARNING = 5  # :v5
    WARNING = 6  # :v6
    WEAK_ERROR = 7  # :v7
    ERROR = 8  # :v8
    CRITICAL = 9  # :v9


class MarkupAnalyzer:
    _mark_pattern_0 = re.compile(r'^:(?:[defilnprstv][0-9]?)+$')
    _mark_pattern_1 = re.compile(r'\w\d?')

    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))

    def extract(self, markup: T.Markup) -> T.Marks:
        defaults = {
            'd': 1,
            'e': 2,
            'f': 1,
            'i': 1,
            'l': 1,
            'n': 1,
            'p': 1,
            'r': 1,
            's': 1,
            't': 2,
            'v': 0,
        }
        out = {}
        for m in self._mark_pattern_1.findall(markup) or ():
            if len(m) == 1:
                out[m[0]] = defaults[m[0]]
            else:
                out[m[0]] = int(m[1:])
        # if out:
        #     dbg_print(dict(out))
        return tp.cast(T.Marks, out)

    def analyze(
        self, markup: T.Markup, _frame: FrameInfo
    ) -> tp.Dict[str, tp.Any]:
        marks = self.postfill(self.extract(markup))
        out: tp.Dict[str, tp.Any] = self.postfill({})  # type: ignore

        # find conflicting marks
        if marks['d']:
            assert not marks['l']
        elif marks['l']:
            assert not marks['d']

        if marks['d']:
            out['d'] = marks['d']
            marks['l'] = 0
            if marks['r'] == 2:
                marks['r'] = 0

        out['e'] = marks['e']
        out['f'] = marks['f']

        # out['i']: Optional[Tuple[int count, str color]]
        if marks['i'] == -1:
            out['i'] = None
        elif marks['i'] == 0:
            counter.reset()
            # out['i'] = (0, 'default')
            out['i'] = None
        elif marks['i'] == 1:
            target_frame = (
                _frame.get_parent(marks['p']) if marks['p'] else _frame
            )
            cnt = counter.update_scoped_index(
                '{}:{}'.format(target_frame.file_path, target_frame.line_number)
            )
            out['i'] = (cnt, counter.get_color_by_frame(target_frame))
        elif marks['i'] == 2:
            target_frame = (
                _frame.get_parent(marks['p']) if marks['p'] else _frame
            )
            cnt = counter.update_scoped_index(
                scope_mgr.current_scope
                or '{}:{}'.format(
                    target_frame.file_path, target_frame.function_name
                )
            )
            out['i'] = (cnt, counter.get_color_by_frame(target_frame))
        elif marks['i'] == 3:
            cnt = counter.update_global_index()
            out['i'] = (cnt, 'red')
        else:
            raise Exception(f':i{marks["i"]}')

        if marks['l'] == 2 and marks['r'] == 2:
            # r2 and l2 have same effect, we remain one of them.
            out['l'] = 0
        else:
            out['l'] = marks['l']

        if config.disable_varnames:
            out['n'] = Mark.NO_VARNAMES
        else:
            if marks['n'] == -1:
                if config.show_varnames and not marks['s']:
                    out['n'] = Mark.SHOW_VARNAMES
                else:
                    out['n'] = Mark.NO_VARNAMES
            else:
                out['n'] = marks['n']

        out['p'] = marks['p']
        out['r'] = marks['r']
        out['s'] = marks['s']

        if marks['t'] == -1:
            out['t'] = None
        elif marks['t'] == 0:
            timer.reset()
            out['t'] = None
        elif marks['t'] == 1:
            out['t'] = timer.current_time()
        elif marks['t'] == 2:
            out['t'] = timer.update_time()
        elif marks['t'] == 3:
            out['t'] = timer.update_scoped_time()
        else:
            raise Exception(f':t{marks["t"]}')

        if marks['v'] == -1:
            out['v'] = None
        else:
            out['v'] = (
                (0, 'bright_black', ''),
                (1, 'magenta', ''),
                (2, 'cyan', ''),
                (3, 'green', 'dim'),
                (4, 'green', ''),
                (5, 'yellow', 'dim'),
                (6, 'yellow', ''),
                (7, 'red', 'dim'),
                (8, 'red', ''),
                ...,  # TODO: (9, 'white on red', '')
            )[marks['v']]

        return out

    def postfill(self, marks: T.Marks) -> T.Marks:
        """
        Fill the missing marks.
        """
        for char in ('d', 'e', 'f', 'i', 'l', 'n', 'p', 'r', 's', 't', 'v'):
            if char not in marks:
                marks[char] = (  # type: ignore
                    -1 if char in ('i', 'n', 't', 'v') else 0
                )
        return marks


markup_analyzer = MarkupAnalyzer()
