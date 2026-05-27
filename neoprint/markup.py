import typing as tp
from re import compile as compile_regex
from time import time
from .config import config
from .frame_info import FrameInfo
from .scope import counter
from .scope import timer


class T:
    Markup = str
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
            't': int,  # timer / timestamp / tabular
            'v': int,  # verbosity / log level
        },
        total=False,
    )


class Mark:
    """
    description: (the asterisk symbol mark means default entry)
            d0  do not show divider line
        *   d1  default divider line
            d2  bold divider line
            e0  show error in plain format
        *   e1  show error with red color
            e2  show exception traceback panel
            e3  show exception traceback with locals
            e4  enter pdb                                      *(not supported)*
            f0  no flush
        *   f1  flush
            f2  flush cutoff
            f3  flush eddy                  *(not a good option, maybe removed)*
            i0  reset index
            i1  line-level index
        *   i2  scoped index
            i3  global index
            l0  no expand object
        *   l1  long / loose / expanded (multiple lines) format
            l2  expand special object
            n0  do not show varnames
        *   n1  show varnames
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
            s2  builtin-like print (remains markup features)
            s3  builtin print
            t0  reset timer
            t1  stop line-level timer and show statistics
        *   t2  stop scoped timer and show statistics
            t3  stop global timer and show statistics
            v0  normal
        *   v1  trace / debug / hint (gray)
            v2  info (blue)
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
    EXPAND = 1  # :l1
    SPECIAL_EXPAND = 2  # :l2

    NO_VARNAMES = 0  # :n0
    SHOW_VARNAMES = 1  # :n1

    SELF_LAYER = 0  # :p0
    PARENT_LAYER = 1  # :p1
    GRANDPARENT_LAYER = 2  # :p2
    GREAT_GRANDPARENT_LAYER = 3  # :p3
    ...  # :p4+

    NO_RICH_FORMAT = 0  # :r0
    RICH_FORMAT = 1  # :r1
    RICH_OBJECT = 2  # :r2

    NO_SHORT_SCHEME = 0  # :s0
    SHORT = 1  # :s1
    SHORTEN = 2  # :s2
    BUILTIN_PRINT = 3  # :s3

    NO_TIMER_STUFF = -1
    RESET_TIMER = 0  # :t0
    STOP_LINE_LEVEL_TIMER = 1  # :t1
    STOP_SCOPED_TIMER = 2  # :t2
    STOP_GLOBAL_TIMER = 3  # :t3

    NORMAL = 0  # :v0
    DEBUG = 1  # :v1
    INFO = 2  # :v2
    WEAK_SUCCESS = 3  # :v3
    SUCCESS = 4  # :v4
    WEAK_WARNING = 5  # :v5
    WARNING = 6  # :v6
    WEAK_ERROR = 7  # :v7
    ERROR = 8  # :v8
    CRITICAL = 9  # :v9


class MarkupAnalyzer:
    _mark_pattern_0 = compile_regex(r'^:(?:[defilnprstv][0-9]?)+$')
    _mark_pattern_1 = compile_regex(r'\w\d?')

    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))

    def analyze(
        self, markup: T.Markup, _frame: FrameInfo
    ) -> tp.Dict[str, tp.Any]:
        marks = self.postfill(self.extract(markup))
        out: tp.Dict[str, tp.Any] = self.postfill({})  # type: ignore

        if marks['d']:
            out['d'] = marks['d']
            marks['l'] = 0

        out['e'] = marks['e']
        out['f'] = marks['f']

        if marks['i'] == -1:
            out['i'] = None
        elif marks['i'] == 0:
            counter.reset()
            out['i'] = 0
        elif marks['i'] == 1:
            cnt = counter.update_scoped_index(
                '{}:{}'.format(_frame.file_path, _frame.line_number)
            )
            out['i'] = cnt
        elif marks['i'] == 2:
            target_frame = (
                _frame.get_parent(marks['p']) if marks['p'] else _frame
            )
            cnt = counter.update_scoped_index(
                '{}:{}'.format(
                    target_frame.file_path, target_frame.function_name
                )
            )
            out['i'] = cnt
        elif marks['i'] == 3:
            cnt = counter.update_global_index()
            out['i'] = cnt
        else:
            raise Exception(f':i{marks["i"]}')

        out['l'] = marks['l']

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
            timer.stop_scoped_timer()
            out['t'] = None

        if marks['v']:
            out['v'] = (
                None,
                ('bright_black', ''),
                ('cyan', ''),
                ('green', 'dim'),
                ('green', ''),
                ('yellow', 'dim'),
                ('yellow', ''),
                ('red', 'dim'),
                ('red', ''),
                ...,  # TODO
            )[marks['v']]

        return out

    def extract(self, markup: T.Markup) -> T.Marks:
        defaults = {
            'd': 1,
            'e': 1,
            'f': 1,
            'i': 2,
            'l': 1,
            'n': 1,
            'p': 1,
            'r': 1,
            's': 1,
            't': 2,
            'v': 1,
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

    def postfill(self, marks: T.Marks) -> T.Marks:
        """
        fill in the missing marks
        """
        for char in ('d', 'e', 'f', 'i', 'l', 'n', 'p', 'r', 's', 't', 'v'):
            if char not in marks:
                marks[char] = (  # type: ignore
                    -1 if char in ('i', 'n', 't') else 0
                )
        return marks


markup_analyzer = MarkupAnalyzer()
