from collections import deque


def qa2ec_0():
    pass


def qa2ec_1():
    pass


queue = deque()
queue.append(qa2ec_0)
queue.appendleft(qa2ec_1)
while queue:
    queue.popleft()()
