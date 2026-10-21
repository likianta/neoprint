import neoprint as np

np.config(show_funcname=True)

def aaa():
    def bbb():
        def ccc():
            np.show('👈 in "ccc" function', ':p0')
            np.show('👈 in "bbb" function', ':p1')
            np.show('👈 in "aaa" function', ':p2')
            np.show('👈 in "<module>" scope', ':p3')

        ccc()
    bbb()
aaa()