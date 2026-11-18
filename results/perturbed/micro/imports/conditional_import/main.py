USE_FAST = False

if USE_FAST:
    from fast import qf87d_0
else:
    from slow import qf87d_0

qf87d_0()
