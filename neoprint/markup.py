import typing as tp
from enum import Enum
from enum import auto
from re import compile as compile_regex
from time import time
from .config import config
from .counter import counter
from .frame_info import FrameInfo


class MarkMeaning(Enum):
    AGRESSIVE_PRUNE = auto()
    BUILTIN_PRINT = auto()
    DIVIDER_LINE = auto()
    EXPAND_OBJECT = auto()
    FLUSH = auto()
    FLUSH_CUTOFF = auto()
    FLUSH_EDDY = auto()
    GLOBAL_INDEX = auto()
    LINE_LEVEL_INDEX = auto()
    MODERATE_PRUNE = auto()
    PARENT_POINTER = auto()
    RESET_INDEX = auto()
    RESET_TIMER = auto()
    RICH_FORMAT = auto()
    RICH_OBJECT = auto()
    SCOPED_INDEX = auto()
    SHOW_VARNAMES = auto()
    STOP_TIMER = auto()
    TABULAR_DATA = auto()
    TEMP_TIMER = auto()
    TRACEBACK_EXCEPTION = auto()
    TRACEBACK_EXCEPTION_WITH_LOCALS = auto()
    VERBOSITY = auto()



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
    MarksMeaning = tp.Dict[MarkMeaning, tp.Any]

    class Counter:
        ColorHex = str
        FrameId = str
        Indent = int
        Index = int
        UniqueId = str

        ScopedIndexes = tp.DefaultDict[UniqueId, Index]
        Uid2ColorHex = tp.DefaultDict[UniqueId, ColorHex]
        UidGenerator = tp.DefaultDict[str, UniqueId]

class E:
    class UnsupportedMarkup(Exception):
        pass



# ------------------------------------------------------------------------------


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
        *   t1  stop timer and show statistics
            t2  temporary timer
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
    STOP_TIMER = 1  # :t1
    TEMP_TIMER = 2  # :t2  # FIXME

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
    """
    readme: prj:/docs/markup.zh.md
    """

    _levels: tp.Tuple[str, ...]
    _mark_pattern_0 = compile_regex(r'^:(?:[defilnprstv][0-9]?)+$')
    _mark_pattern_1 = compile_regex(r'\w\d?')
    _simple_time: float
    _temp_time: float

    def __init__(self) -> None:
        self._simple_time = time()
        self._temp_time = time()

    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))

    def analyze(self, markup: T.Markup, **kwargs) -> T.MarksMeaning:
        marks = self.postfill(self.extract(markup))
        out = {}

        if marks['d']:
            out[MarkMeaning.DIVIDER_LINE] = marks['d']

        if marks['e']:
            if marks['e'] == 1:
                out[MarkMeaning.TRACEBACK_EXCEPTION] = True
            elif marks['e'] == 2:
                out[MarkMeaning.TRACEBACK_EXCEPTION_WITH_LOCALS] = True
            else:
                raise E.UnsupportedMarkup(f':e{marks["e"]}')

        if marks['f']:
            if marks['f'] == 1:
                out[MarkMeaning.FLUSH] = True
            elif marks['f'] == 2:
                out[MarkMeaning.FLUSH_CUTOFF] = True
            elif marks['f'] == 3:
                out[MarkMeaning.FLUSH_EDDY] = True
            else:
                raise E.UnsupportedMarkup(f':f{marks["f"]}')

        if marks['i'] >= 0:
            if marks['i'] == 0:
                self._counter.reset_all_indexes()
                out[MarkMeaning.RICH_FORMAT] = True
                out[MarkMeaning.RESET_INDEX] = 0
            elif marks['i'] == 1:
                out[MarkMeaning.LINE_LEVEL_INDEX] = (
                    self._counter.update_line_level_index(kwargs['frame_info'])
                )
            elif marks['i'] == 2:
                out[MarkMeaning.INTELLIGENT_INDEX] = (
                    self._counter.update_scoped_index(kwargs['frame_info'])
                )
            elif marks['i'] == 3:
                out[MarkMeaning.GLOBAL_INDEX] = (
                    self._counter.update_global_index()
                )
            else:
                raise E.UnsupportedMarkup(f':i{marks["i"]}')

        if marks['l']:
            out[MarkMeaning.EXPAND_OBJECT] = marks['l'] + 1  # 1 or 2

        if marks['n'] == -1:
            if marks['s']:
                out[MarkMeaning.SHOW_VARNAMES] = False
            else:
                out[MarkMeaning.SHOW_VARNAMES] = config.show_varnames
        else:
            out[MarkMeaning.SHOW_VARNAMES] = bool(marks['n'])

        if marks['p']:
            out[MarkMeaning.PARENT_POINTER] = marks['p']

        if marks['r']:
            if marks['r'] == 1:
                out[MarkMeaning.RICH_FORMAT] = True
            elif marks['r'] == 2:
                out[MarkMeaning.RICH_OBJECT] = True
            else:
                raise E.UnsupportedMarkup(f':r{marks["r"]}')

        if marks['s']:
            if marks['s'] == 1:
                out[MarkMeaning.MODERATE_PRUNE] = True
            elif marks['s'] == 2:
                out[MarkMeaning.AGRESSIVE_PRUNE] = True
            elif marks['s'] == 3:
                out[MarkMeaning.BUILTIN_PRINT] = True
            else:
                raise E.UnsupportedMarkup(f':s{marks["s"]}')

        if marks['t'] >= 0:
            if marks['t'] == 0:
                out[MarkMeaning.RICH_FORMAT] = True
                t = self._simple_time = time()
                out[MarkMeaning.RESET_TIMER] = t
            elif marks['t'] == 1:
                out[MarkMeaning.RICH_FORMAT] = True
                start, end = self._simple_time, time()
                out[MarkMeaning.STOP_TIMER] = (start, end)
                self._simple_time = end
            elif marks['t'] == 2:
                out[MarkMeaning.RICH_FORMAT] = True
                start, end = self._temp_time, time()
                out[MarkMeaning.TEMP_TIMER] = (start, end)
                self._temp_time = end
            elif marks['t'] == 3:
                out[MarkMeaning.TABULAR_DATA] = True
            else:
                raise E.UnsupportedMarkup(f':t{marks["t"]}')

        if marks['v']:
            out[MarkMeaning.VERBOSITY] = marks['v']

        return out
    
    def analyze2(self, markup: T.Markup, _frame: FrameInfo) -> tp.Dict[str, tp.Any]:
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
                '{}:{}'.format(
                    _frame.file_path, _frame.line_number
                )
            )
            out['i'] = cnt
        elif marks['i'] == 2:
            target_frame = tp.cast(
                FrameInfo, 
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
        out['t'] = marks['t']
        
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
                ...  # TODO
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
            't': 1,
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
