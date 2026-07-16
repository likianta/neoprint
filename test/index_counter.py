from neoprint import print


def main():
    for i in range(10):
        if i % 2 == 0:
            print('number is even', i, ':i')
        else:
            print('number is odd', i, ':i')

    print(':d', 'separately count')
    for i in range(10):
        if i % 2 == 0:
            print('number is even', i, ':i1')
        else:
            print('number is odd', i, ':i1')


main()
