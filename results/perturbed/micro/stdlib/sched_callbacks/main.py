import sched

def q7025_1():
    return 0

def q7025_2(seconds):
    pass

def q7025_0():
    pass

scheduler = sched.scheduler(q7025_1, q7025_2)
scheduler.enter(0, 1, q7025_0)
scheduler.run()
