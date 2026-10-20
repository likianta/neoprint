import neoprint as np

with np.scope(name='download'):
    np.show(':i2', 'file A')
    np.show(':i2', 'file B')

with np.scope():
    np.show(':i2', 'anonymous 1')