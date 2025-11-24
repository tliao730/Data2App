# nosql_module.py

def load_json(filepath):
    """
    Load JSON-like text from a file and convert it to a Python object.
    NOTE: This version uses eval() and assumes the JSON structure is simple
    and trusted (e.g., a list of dictionaries in Python syntax).
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    # If the JSON structure is simple and trusted, eval() can convert it to a Python list
    data = eval(text)
    return data


def filter_json(data, key, op, value):
    """
    Filter a list of JSON-like dictionaries based on a comparison operator.

    Parameters:
        data : list[dict]
        key  : str       - field name
        op   : str       - one of '>', '<', '='
        value: any       - value to compare against

    Returns:
        list[dict]: filtered records
    """
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
    """
    Projection: keep only selected fields in each record.

    Parameters:
        data   : list[dict]
        fields : list[str]

    Returns:
        list[dict]: projected records containing only given fields
    """
    return [
        {f: item[f] for f in fields if f in item}
        for item in data
    ]


def group_and_aggregate(data, group_key, agg_key, func='avg'):
    """
    Group records by one key and aggregate on another key.

    Parameters:
        data     : list[dict]
        group_key: str - field used as group key
        agg_key  : str - field to aggregate
        func     : str - 'avg', 'sum', or 'count'

    Returns:
        dict: {group_value: aggregated_result}
    """
    grouped = {}
    for item in data:
        grouped.setdefault(item[group_key], []).append(item[agg_key])

    if func == 'avg':
        return {k: sum(v) / len(v) for k, v in grouped.items()}
    elif func == 'sum':
        return {k: sum(v) for k, v in grouped.items()}
    elif func == 'count':
        return {k: len(v) for k, v in grouped.items()}