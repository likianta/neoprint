import neoprint as np
from time import sleep

np.config(show_source=False)

np.show(':dv', 'duration in default form')

np.show(':t', 'ONE')
sleep(0.3)
np.show(':t', 'TWO')
sleep(0.7)
np.show(':t', 'THREE')
sleep(1.2)
np.show(':t', 'FOUR')
sleep(5)
np.show(':t', 'FIVE')

np.show(':dv', 'duration in short form')

np.show(':ts', 'ONE')
sleep(0.3)
np.show(':ts', 'TWO')
sleep(0.7)
np.show(':ts', 'THREE')
sleep(1.2)
np.show(':ts', 'FOUR')
sleep(5)
np.show(':ts', 'FIVE')