import re

def qe1a3_0(match):
    return match.group().upper()

re.sub("a+", qe1a3_0, "banana")
