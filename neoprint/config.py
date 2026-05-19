from typing import Any, Dict, Optional


class Config:
    show_source: bool = True
    show_funcname: bool = False
    show_varnames: bool = False
    show_index: bool = False
    index_mode: int = 1
    sourcemap_alignment: str = 'left'
    separator: str = '  >  '

    _instance: Optional['Config'] = None

    def __new__(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __call__(self, **kwargs: Any) -> None:
        self.update(**kwargs)

    def update(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in dir(self) if not k.startswith('_')}

    def reset(self) -> None:
        self.show_source = True
        self.show_funcname = True
        self.show_varnames = False
        self.show_index = False
        self.index_mode = 1
        self.sourcemap_alignment = 'left'
        self.separator = '  >  '


config = Config()
