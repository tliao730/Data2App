def _attempt_convert_type(value_str):
    """Automatically convert string values to appropriate data types"""
    # Handle empty strings
    if not value_str or value_str.strip() == '':
        return None
    
    value_str = value_str.strip()
    
    # Handle quoted strings
    if value_str.startswith('"') and value_str.endswith('"'):
        return value_str[1:-1]
    
    # Try converting to integer
    try:
        return int(value_str)
    except ValueError:
        pass
    
    # Try converting to float
    try:
        return float(value_str)
    except ValueError:
        pass
    
    # Handle boolean values
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'
    
    # Return original string
    return value_str

def parse_csv_line(line, separator=",", quote_char='"'):
    """
    Parse a CSV line while properly handling separators inside quotes
    """
    data_per_row = []
    current_value = ""
    in_quotes = False
    
    for char in line:
        if char == quote_char:
            in_quotes = not in_quotes
        elif char == separator and not in_quotes:
            data_per_row.append(current_value)
            current_value = ""
        else:
            current_value += char
    
    # Add the last value
    data_per_row.append(current_value)
    return data_per_row