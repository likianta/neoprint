import os
import sys
import typing as tp

from .console import dprint

# CWD = os.getcwd().replace('\\', '/')


class _PathGlobConfig:
    def __init__(self) -> None:
        self.main_paths = []
        # main path illustration:
        #     __main__ module path: /projects/example/neoprint/__main__.py
        #     working directory   : /projects/example
        #     relative path       : neoprint/__main__.py
        #     main path added     : /projects/example/neoprint/
        dprint(sys.modules['__main__'])
        if hasattr(sys.modules['__main__'], '__file__'):
            self.main_paths.append(
                (
                    os.path.join(
                        os.getcwd(),
                        os.path.relpath(
                            tp.cast(
                                str,
                                sys.modules['__main__'].__file__
                                # if hasattr(sys.modules['__main__'], '__file__')
                                # else sys.modules['__main__'].__path__[0],
                                # else sys.modules['__main__'].__spec__.origin,
                            ),
                            os.getcwd(),
                        ).split(os.sep, 1)[0],
                    )
                ).replace('\\', '/')
                + '/'
            )
        else:  # e.g. <module '__main__' of _frozen_importlib.BuiltinImporter>
            self.main_paths.append(os.getcwd().replace('\\', '/') + '/')
        dprint(self.main_paths)
        self._cache = {}  # TODO: when main paths changed, cache will be reset.

    def is_external_path(self, path: str) -> bool:
        if path not in self._cache:
            self._cache[path] = any(path.startswith(p) for p in self.main_paths)
        return not self._cache[path]


path_glob = _PathGlobConfig()
