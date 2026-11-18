def qf37f_0(person):
    return person[1]

def qf37f_1(person):
    return person[0]

def qf37f_3(people):
    return min(people, key=qf37f_0)

def qf37f_2(people):
    return max(people, key=qf37f_1)

people = [("ann", 3), ("bob", 1)]
qf37f_3(people)
qf37f_2(people)
