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
        np.show(aaa, ':n')
        np.show(aaa, ':n1')
    ]

Index:
    [
        # level function
        # ----- ---------------------------
        # :i0   reset index
        # :i1   line-level index
        # :i2   scope-level index (default)
        # :i3   global-level index

        # foo.py
        np.show('first', ':i')
        np.show('second', ':i')
        np.show('third', ':i')

        def bar():
            np.show('first', ':i')
            np.show('second', ':i')
            np.show('third', ':i')

        with np.scope():
            np.show('first', ':i')
            np.show('second', ':i')
            np.show('third', ':i')

        for _ in range(10):
            np.show('increase index at each call', ':i1')
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

Color verbosity:
    [
        np.show('normal text', ':v0')
        np.show('gray text for hint or weak tip', ':v1')
        np.show('cyan text for infomation', ':v2')
        np.show('dim green for weak success', ':v3')
        np.show('accent green for success', ':v4')
        np.show('dim yellow for weak warning', ':v5')
        np.show('accent yellow for warning', ':v6')
        np.show('dim red for weak error', ':v7')
        np.show('accent red for error', ':v8')
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
