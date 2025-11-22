# nosql_module.py

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    # 如果 JSON 結構單純，可以用 eval() 轉為 Python list
    data = eval(text)
    return data


def filter_json(data, key, op, value):
    result = []
    for item in data:
        if op == '>' and item[key] > value:
            result.append(item)
        elif op == '<' and item[key] < value:
            result.append(item)
        elif op == '=' and item[key] == value:
            result.append(item)
    return result


def project_json(data, fields):
    return [{f: item[f] for f in fields if f in item} for item in data]


def group_and_aggregate(data, group_key, agg_key, func='avg'):
    grouped = {}
    for item in data:
        grouped.setdefault(item[group_key], []).append(item[agg_key])

    if func == 'avg':
        return {k: sum(v) / len(v) for k, v in grouped.items()}
    elif func == 'sum':
        return {k: sum(v) for k, v in grouped.items()}
    elif func == 'count':
        return {k: len(v) for k, v in grouped.items()}