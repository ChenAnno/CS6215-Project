def q2d41_1():
    pass

def q2d41_2():
    pass

def q2d41_0(command):
    match command:
        case "start":
            return q2d41_1
        case "stop":
            return q2d41_2

q2d41_0("stop")()
