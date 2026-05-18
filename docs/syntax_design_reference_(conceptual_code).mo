[# Syntax Design Reference (Conceptual Code)]

Elevate frame pointer:
    [
        np.show('aaa', 'bbb', parent=1)
        np.show('aaa', 'bbb', parent=2)
        np.show('aaa', 'bbb', parent=3)
        ...

        np.show('aaa', 'bbb', ':p1')
        np.show('aaa', 'bbb', ':p2')
        np.show('aaa', 'bbb', ':p3')
        ...
    ]

Show varnames:
    [
        aaa = 'Alpha'
        np.show(aaa, varnames=1)
        np.show(aaa, ':v')
        np.show(aaa, ':v1')
    ]

Index:
    [
        np.show('aaa', index=1)
        np.show('aaa', ':i')
        #   level   function
        #   0       do not show index
        #   1       crease index at each call
        #   2       inherit last index scope
        #   3       global index
        np.show('aaa', ':i0')
        np.show('aaa', ':i1')
        np.show('aaa', ':i2')
        np.show('aaa', ':i3')

        # scoped index
        npi = np.index()
        for i in range(10):
            if ...:
                npi.show('aaa')
            else:
                npi.show('bbb')

        with np.indexing():
            np.show('aaa')
            np.show('bbb')
    ]

Progress:
    [
        for item in np.progress(range(10)):
            ...

        with np.progressing() as prog:
            for item in range(10):
                prog.update(...)

        # inline progress
        with np.progressing():
            np.show(...)
    ]

Color:
    [
        np.show('normal text', ':c0')
        np.show('gray text for hint or weak tip', ':c1')
        np.show('cyan text for infomation', ':c2')
        np.show('dim green for weak success', ':c3')
        np.show('accent green for success', ':c4')
        np.show('dim yellow for weak warning', ':c5')
        np.show('accent yellow for warning', ':c6')
        np.show('dim red for weak error', ':c7')
        np.show('accent red for error', ':c8')
        #   shorthand: 1/3/5/7 are dim colors, 2/4/6/8 are accent colors
    ]

Configure style:
    [
        np.config_print_pattern(
            '{path_type3}'
            '{separator_type1}'
            '{line_number}'
            '{space}'
            '{funcname}'
            '{space}'
            '{separator_type2}'
            '{message}'
        )
        #   note: if message is in multi-line format, it will be started from 
        #   the second row with a smart indent.
        np.config_exception_handler(handler='rich')
        np.config_exception_handler(handler='builtin')
    ]

Scoped:
    [
        with np.mute():
            ...
        
        with np.scope(parent=1):
            ...
    ]
