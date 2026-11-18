import bisect
import heapq

def q6471_0(task):
    return task[0]

heapq.nsmallest(1, [(2, "b"), (1, "a")], key=q6471_0)
bisect.bisect([(1, "a")], 1, key=q6471_0)
