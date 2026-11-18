import os
import os.path as osp
from os import path

join = os.path.join

def q9273_3():
    os.path.join("a", "b")

def q9273_2():
    path.join("a", "b")

def q9273_1():
    osp.join("a", "b")

def q9273_0():
    join("a", "b")

q9273_3()
q9273_2()
q9273_1()
q9273_0()
