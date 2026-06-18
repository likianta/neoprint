import os
from functools import cache

CWD = os.getcwd().replace('\\', '/')


class _PathGlobConfig:
    internal_paths = [CWD + '/']
    # external_paths = []
    
    @cache
    def is_external_path(self, path: str) -> bool:
        return not any(path.startswith(p) for p in self.internal_paths)


path_glob = _PathGlobConfig()
