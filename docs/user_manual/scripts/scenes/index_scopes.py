import neoprint as np
from neoprint.scope import counter as index_counter

COLORS = {'foo': '#8aafde', 'bar': '#ffcf88'}

_get_color_by_id = index_counter.get_color_by_id

def get_color_by_id(id: str) -> str:
    for name, color in COLORS.items():
        if id.endswith(':' + name):
            return color
    return _get_color_by_id(id)

setattr(index_counter, 'get_color_by_id', get_color_by_id)

np.config(show_funcname=True)

def foo():
    np.show(':i2', 'file A')
    np.show(':i2', 'file B')
    np.show(':i2', 'file C')
    np.show(':i2', 'file D')
    np.show(':i2', 'file E')

def bar():
    np.show(':i2', 'anonymous 1')
    np.show(':i2', 'anonymous 2')

foo()
bar()