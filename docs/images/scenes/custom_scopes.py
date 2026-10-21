import neoprint as np
from neoprint.scope import counter as index_counter

COLORS = ['#8aafde', '#ffcf88']
_assigned = {}

def get_color_by_id(id: str) -> str:
    if id not in _assigned:
        _assigned[id] = COLORS[len(_assigned) % len(COLORS)]
    return _assigned[id]

setattr(index_counter, 'get_color_by_id', get_color_by_id)

with np.scope():
    np.show(':i2', 'anonymous scope - item 1')
    np.show(':i2', 'anonymous scope - item 2')

with np.scope(name='MyScope'):
    np.show(':i2', 'MyScope - item 1')
    np.show(':i2', 'MyScope - item 2')