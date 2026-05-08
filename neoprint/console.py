import rich
import sys
from rich.traceback import Traceback
from loguru import logger as _loguru_logger

# remove the pre-configured default handler
_loguru_logger.remove()
_loguru_logger.add(
    sys.stdout,
    format=(
        '<magenta>{name}</magenta>'
        ':<cyan>{function}</cyan>'
        ':<green>{line}</green>'
        ' <light-black>|</light-black>'
        ' <level>{message}</level>'
    ),
)

_rich_console = rich.get_console()


def exception(e: Exception, show_locals: bool = False) -> None:
    _rich_console.print(
        Traceback.from_exception(
            type(e), e, e.__traceback__, show_locals=show_locals
        )
    )


critical = exception  # alias
debug = _loguru_logger.debug
error = _loguru_logger.error
info = _loguru_logger.info
print = info  # alias
show = info  # alias
warning = _loguru_logger.warning
