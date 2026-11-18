import json

def qdc8f_0(obj):
    return obj

json.loads('{"a": 1}', object_hook=qdc8f_0)
