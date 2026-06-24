from .base import T
from .base import TextObject
from ..config import config
from ..frame_info import FrameInfo
from ..path_scope import path_glob
from ..render import render


class Source(TextObject):
    def __init__(self, frame: FrameInfo) -> None:
        self._path = frame.file_path
        self._pname = '[{}]'.format(frame.package_name)
        self._fname = frame.file_name
        if config.sourcemap_alignment == 'left':
            self._lineno = self._pad_lineno(frame.line_number)
        else:
            self._lineno = str(frame.line_number)

    def render(
        self,
        name_format='filename:lineno',
        external_name_format='[libname]:filename:lineno',
        color_code_scheme: T.CodeScheme = 'none',
    ) -> str:
        """
        name_style:
            'filename': e.g. 'main.py'
            'relpath': e.g. 'example/main.py'
        name_style_for_external_lib:
            'follow_name_style': follow `name_style` value.
            'libname_relpath': show `[{libname}]/{relpath}:{lineno}`
            'libname_filename': show `[{libname}]/{filename}:{lineno}`
        shrink_relpath_with_separator:
            '~': show `[{libname}]/~/{filename}:{lineno}`.
                e.g. "[lk_utils]/~/promise.py:10".
            '~x': show `[{libname}]/~{level_count}/{filename}:{lineno}`.
                e.g. "[lk_utils]/~1/promise.py:10".
            '...': show `[{libname}]/.../{filename}:{lineno}`.
                e.g. "[lk_utils]/.../promise.py:10".
            '...x': show `[{libname}]/...{level_count}/{filename}:{lineno}`.
                e.g. "[lk_utils]/...1/promise.py:10".
        """
        # TODO
        assert name_format == 'filename:lineno'
        assert external_name_format == '[libname]:filename:lineno'
        if path_glob.is_external_path(self._path):
            return render(
                (self._pname, 'magenta'),
                (':', 'blue', 'dim'),
                (self._fname, 'blue'),
                (':', 'green', 'dim'),
                (self._lineno, 'green'),
                code_scheme=color_code_scheme,
            )
        else:
            return render(
                (self._fname, 'blue'),
                (':', 'green', 'dim'),
                (self._lineno, 'green'),
                code_scheme=color_code_scheme,
            )

    def _pad_lineno(self, number: int, width: int = 3) -> str:
        a, b = divmod(len(str(number)), width)
        return str(number).ljust(width * (a + (1 if b else 0)))
