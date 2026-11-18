def qbac1_0():
    pass

def qbac1_1():
    pass

match [qbac1_0, qbac1_1]:
    case [_, _] as pair:
        pair[0]()
