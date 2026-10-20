import neoprint as np


def aaa():
    def bbb():
        def ccc():
            np.show('DDD', ':p0')
            np.show('CCC', ':p1')
            np.show('BBB', ':p2')
            np.show('AAA', ':p3')

        ccc()
    bbb()
aaa()