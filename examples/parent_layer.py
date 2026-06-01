import neoprint as np  # ln1

def aaa():  # ln3
    def bbb():  # ln4
        def ccc():  # ln5
            def ddd():  # ln6
                np.show('DDD', ':p0')  # ln7
                np.show('CCC', ':p1')  # ln8
                np.show('BBB', ':p2')  # ln9
                np.show('AAA', ':p3')  # ln10
                np.show('<module>', ':p4')  # ln11
                # np.show('???', ':p5')  # ln12
            ddd()  # ln13
        ccc()  # ln14
    bbb()  # ln15
aaa()  # ln16
