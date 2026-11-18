import json

def q99e8_0(value):
    return sorted(value)

json.dumps({1, 2}, default=q99e8_0)
