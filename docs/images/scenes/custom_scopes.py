import neoprint as np

with np.scope():
    np.show(':i2', 'anonymous scope - item 1')
    np.show(':i2', 'anonymous scope - item 2')

with np.scope(name='MyScope'):
    np.show(':i2', 'MyScope - item 1')
    np.show(':i2', 'MyScope - item 2')