from neoprint import print
from time import sleep

print(':dt1v2', 'START')

print(':t', 'ONE')
sleep(0.3)
print(':t', 'TWO')
sleep(0.7)
print(':t', 'THREE')
sleep(1.2)
print(':t', 'FOUR')
sleep(5)
print(':t', 'FIVE')

print(':dt3', 'END')
