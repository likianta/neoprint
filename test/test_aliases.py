from neoprint import print, debug, info, success, warning, error

print('hello', 'world')
debug('user has came here, say hello to him')
info('welcome to the city!')
success('successfully create the file')
warning('target file exists, will overwrite it')
error('failed create the file')

try:
    1 / 0
except ZeroDivisionError as e:
    error(e, ':e2')
