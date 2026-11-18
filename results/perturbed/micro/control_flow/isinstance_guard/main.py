import json


def q92d1_0(text):
    data = json.loads(text)
    if not isinstance(data, dict):
        return None
    return data.items()


q92d1_0('{"a": 1}')
