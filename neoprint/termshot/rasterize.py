import math
import re
import shutil
import subprocess
import typing as tp
import xml.etree.ElementTree as ET
from pathlib import Path

_BROWSERS = (
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
)
#   browsers' names to search for in PATH.
_BROWSER_NAMES = (
    'google-chrome',
    'google-chrome-stable',
    'chromium',
    'chromium-browser',
    'chrome',
    'msedge',
    'microsoft-edge',
)

#   the metrics rich bakes into its svg export. see `Console.save_svg`.
_SVG_NS = 'http://www.w3.org/2000/svg'
_BASE_FONT_SIZE = 20.0
_BASE_LINE_HEIGHT = 24.4
#   padding (8 + 8 + 40 + 8) plus the 1px margin on each side.
_SVG_PADDING_WIDTH = 18.0
_SVG_PADDING_HEIGHT = 50.0


def svg_to_png(
    svg: tp.Union[str, Path],
    png: tp.Union[str, Path],
    *,
    scale: int = 2,
    browser: tp.Optional[str] = None,
) -> None:
    """
    Rasterize an svg with a headless Chrome / Edge / Chromium.

    params:
        scale: the device scale factor. 2 gives a crisp image on retina
            screens.
        browser: the path or name of the browser to use. when omitted, a
            common Chrome / Edge location is searched, then PATH.
    """
    if scale < 1:
        raise ValueError('scale should be >= 1, got {}'.format(scale))

    svg_path = Path(svg)
    png_path = Path(png)
    png_path.parent.mkdir(parents=True, exist_ok=True)

    width, height = _viewbox_size(svg_path)
    command = [
        find_browser(browser),
        '--headless=new',
        '--disable-gpu',
        '--hide-scrollbars',
        '--force-device-scale-factor={}'.format(scale),
        '--window-size={},{}'.format(width, height),
        '--screenshot={}'.format(png_path.resolve()),
        svg_path.resolve().as_uri(),
    ]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(
            'failed to rasterize {}:\n{}'.format(
                svg_path, result.stderr.decode('utf-8', 'replace').strip()
            )
        )


def find_browser(explicit: tp.Optional[str] = None) -> str:
    """Find an executable that can rasterize an svg headlessly."""
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return str(path)
        found = shutil.which(explicit)
        if found:
            return found
        raise FileNotFoundError('browser not found: {!r}'.format(explicit))

    for candidate in _BROWSERS:
        if Path(candidate).is_file():
            return candidate

    for name in _BROWSER_NAMES:
        found = shutil.which(name)
        if found:
            return found

    raise RuntimeError(
        'no Chrome, Edge, or Chromium found. install one, or pass an '
        'explicit browser path to `save_png(..., browser=...)`.'
    )


def apply_style(
    svg: tp.Union[str, Path],
    *,
    font: tp.Union[str, tp.Sequence[str], None] = None,
    font_size: float = _BASE_FONT_SIZE,
    line_height: float = _BASE_LINE_HEIGHT,
    ligatures: bool = True,
) -> None:
    """
    Rewrite the generated svg to use a local font and custom metrics.

    rich exports an svg that embeds a CDN hosted Fira Code and bakes the
    geometry of a 20px font with a 24.4px line height into every coordinate.
    This function replaces the font declaration and, when the size or the
    line height differ from those defaults, rescales the geometry so rows,
    backgrounds, and text keep their alignment.

    params:
        font: a locally installed font name, or a sequence of names used as
            fallbacks. when omitted, the embedded Fira Code is kept.
        font_size: the font size in px.
        line_height: the line height in px. must be >= `font_size`.
        ligatures: whether to enable font ligatures.
    """
    if (
        not font
        and font_size == _BASE_FONT_SIZE
        and line_height == _BASE_LINE_HEIGHT
        and ligatures
    ):
        return

    path = Path(svg)
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(str(path), parser=parser)
    root = tree.getroot()

    _rewrite_style(root, font, font_size, line_height, ligatures)
    _rescale_geometry(root, font_size, line_height)

    ET.register_namespace('', _SVG_NS)
    ET.indent(tree, space='    ')
    tree.write(str(path), encoding='utf-8', xml_declaration=False)


def _rewrite_style(
    root: ET.Element,
    font: tp.Union[str, tp.Sequence[str], None],
    font_size: float,
    line_height: float,
    ligatures: bool,
) -> None:
    style = root.find(_tag('style'))
    if style is None or style.text is None:
        return

    text = style.text
    if font:
        text = re.sub(r'\s*@font-face \{.*?\}', '', text, flags=re.S)
        family = ', '.join(
            "'{}'".format(name.replace("'", "\\'"))
            for name in ([font] if isinstance(font, str) else font)
        )
        family += ', monospace'
    else:
        family = 'Fira Code, monospace'

    text = text.replace(
        'font-family: Fira Code, monospace;',
        'font-family: {family};\n'
        '        font-variant-ligatures: {variant};\n'
        '        font-feature-settings: {features};'.format(
            family=family,
            variant='normal' if ligatures else 'none',
            features=(
                '"liga" 1, "calt" 1' if ligatures else '"liga" 0, "calt" 0'
            ),
        ),
    )
    text = text.replace(
        'font-size: {}px;'.format(_fmt(_BASE_FONT_SIZE)),
        'font-size: {}px;'.format(_fmt(font_size)),
    )
    text = text.replace(
        'line-height: {}px;'.format(_fmt(_BASE_LINE_HEIGHT)),
        'line-height: {}px;'.format(_fmt(line_height)),
    )
    style.text = text


def _rescale_geometry(
    root: ET.Element, font_size: float, line_height: float
) -> None:
    if font_size == _BASE_FONT_SIZE and line_height == _BASE_LINE_HEIGHT:
        return

    sx = font_size / _BASE_FONT_SIZE
    sy = line_height / _BASE_LINE_HEIGHT

    viewbox = (root.get('viewBox') or '').split()
    if len(viewbox) != 4:
        raise ValueError('cannot read the viewBox from the svg')
    width, height = float(viewbox[2]), float(viewbox[3])
    new_width = _round((width - _SVG_PADDING_WIDTH) * sx + _SVG_PADDING_WIDTH)
    new_height = _round(
        (height - _SVG_PADDING_HEIGHT) * sy + _SVG_PADDING_HEIGHT
    )
    root.set('viewBox', '0 0 {} {}'.format(_fmt(new_width), _fmt(new_height)))

    for elem in root.iter():
        if not isinstance(elem.tag, str):
            continue
        tag = _local(elem.tag)
        if tag == 'rect':
            if elem.get('rx') is not None:
                #   the window chrome
                elem.set('x', '1')
                elem.set('y', '1')
                elem.set('width', _fmt(new_width - 2))
                elem.set('height', _fmt(new_height - 2))
            elif elem.get('shape-rendering') == 'crispEdges':
                #   a row background
                _scale_row_rect(elem, sx, sy, line_height)
        elif tag == 'clipPath':
            rect = elem.find(_tag('rect'))
            if rect is None:
                continue
            if (elem.get('id') or '').endswith('-clip-terminal'):
                _scale_size(rect, sx, sy)
            else:
                _scale_row_rect(rect, sx, sy, line_height)
        elif tag == 'text':
            if (elem.get('class') or '').endswith('-title'):
                elem.set('x', str(int((new_width - 2) // 2)))
            else:
                _scale_text(elem, sx, sy)


def _scale_size(rect: ET.Element, sx: float, sy: float) -> None:
    width = _get_float(rect, 'width')
    height = _get_float(rect, 'height')
    rect.set('width', _fmt((width + 1) * sx - 1))
    rect.set('height', _fmt((height + 1) * sy - 1))


def _scale_row_rect(
    rect: ET.Element, sx: float, sy: float, line_height: float
) -> None:
    x = _get_float(rect, 'x')
    y = _get_float(rect, 'y')
    width = _get_float(rect, 'width')
    rect.set('x', _fmt(x * sx))
    rect.set('y', _fmt((y - 1.5) * sy + 1.5))
    rect.set('width', _fmt(width * sx))
    rect.set('height', _fmt(line_height + 0.25))


def _scale_text(text: ET.Element, sx: float, sy: float) -> None:
    x = _get_float(text, 'x')
    y = _get_float(text, 'y')
    text_length = _get_float(text, 'textLength')
    text.set('x', _fmt(x * sx))
    text.set('y', _fmt(y * sy))
    text.set('textLength', _fmt(text_length * sx))


def _tag(name: str) -> str:
    return '{{{}}}{}'.format(_SVG_NS, name)


def _local(tag: str) -> str:
    return tag.rsplit('}', 1)[-1]


def _get_float(elem: ET.Element, name: str) -> float:
    value = elem.get(name)
    if value is None:
        raise ValueError('missing {!r} on <{}>'.format(name, _local(elem.tag)))
    return float(value)


def _round(value: float) -> float:
    return round(value, 2)


def _fmt(value: float) -> str:
    return format(_round(value), 'g')


def _viewbox_size(svg: Path) -> tp.Tuple[int, int]:
    match = re.search(
        r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text(encoding='utf-8')
    )
    if not match:
        raise ValueError('cannot read the viewBox from {}'.format(svg))
    return math.ceil(float(match.group(1))), math.ceil(float(match.group(2)))
