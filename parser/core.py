from utils import parse_csv_line

class DataFrame:
    def __init__(self, data_dict):
        """
        Initialize DataFrame with a dictionary of columns
        data_dict: {'column1': [values], 'column2': [values]}
        """
        if not data_dict:
            raise ValueError("Cannot create DataFrame from empty data")
        
        # Ensure all columns have consistent row count
        lengths = [len(v) for v in data_dict.values()]
        if len(set(lengths)) > 1:
            mismatched = {k: len(v) for k, v in data_dict.items()}
            raise ValueError(f"All columns must have the same length. Mismatched lengths: {mismatched}")
        
        self.data = data_dict
        self.columns = list(data_dict.keys())
        self.row_count = lengths[0] if lengths else 0
    
    def __repr__(self):
        """Return a formatted string representation of the DataFrame (similar to pandas)"""
        if self.row_count == 0:
            return "Empty DataFrame"
        
        # Compute column widths
        col_widths = {}
        for col in self.columns:
            max_width = len(col)
            for val in self.data[col][:10]:  # Only check the first 10 rows
                max_width = max(max_width, len(str(val)))
            col_widths[col] = min(max_width, 20)  # Limit width
        
        result = []
        
        # Header
        header = " | ".join(col.ljust(col_widths[col]) for col in self.columns)
        result.append(header)
        result.append("-" * len(header))
        
        # Data rows (up to 10)
        display_rows = min(10, self.row_count)
        for i in range(display_rows):
            row = []
            for col in self.columns:
                val = str(self.data[col][i])
                if len(val) > col_widths[col]:
                    val = val[:col_widths[col]-3] + "..."
                row.append(val.ljust(col_widths[col]))
            result.append(" | ".join(row))
        
        if self.row_count > 10:
            result.append(f"\n... {self.row_count - 10} more rows")
        
        result.append(f"\nShape: ({self.row_count} rows, {len(self.columns)} columns)")
        
        return "\n".join(result)
    
    def __getitem__(self, key):
        """
        Support column selection, multiple column selection, and boolean indexing
        """
        if isinstance(key, str):
            return self.data[key]  # Single column
        
        elif isinstance(key, list) and all(isinstance(k, str) for k in key):
            return DataFrame({col: self.data[col] for col in key})  # Subset of columns
        
        elif isinstance(key, list) and all(isinstance(k, bool) for k in key):
            # Boolean filter
            if len(key) != self.row_count:
                raise ValueError("Boolean index length mismatch")
            
            new_data = {col: [] for col in self.columns}
            for i, keep in enumerate(key):
                if keep:
                    for col in self.columns:
                        new_data[col].append(self.data[col][i])
            
            return DataFrame(new_data)
        
        else:
            raise TypeError(f"Invalid indexing type: {type(key)}")
    
    def __len__(self):
        return self.row_count

    # ==================== 1. Filtering ====================
    
    def filter(self, condition):
        """
        Filter rows by a condition
        
        parameters:
            condition: function or boolean list
                - function: lambda row: row['Age'] > 18
                - list: [True, False, True, ...]
        
        Returns:
            DataFrame: filtered result
        """
        if callable(condition):
            keep_rows = []
            for i in range(self.row_count):
                row = {col: self.data[col][i] for col in self.columns}
                keep_rows.append(condition(row))
            return self[keep_rows]
        
        elif isinstance(condition, list) and all(isinstance(k, bool) for k in condition):
            return self[condition]
        
        else:
            raise TypeError("Condition must be callable or a list of booleans")
    
    # ==================== 2. Projection ====================
    
    def select(self, columns):
        """
        Select one or more columns
        
        Parameters:
            columns: str or list
        
        Returns:
            DataFrame
        """
        if isinstance(columns, str):
            columns = [columns]
        
        return self[columns]
    
    # ==================== 3. GroupBy ====================
    
    def groupby(self, by):
        """
        Group rows by one or more columns
        
        Parameters:
            by: str or list
        
        Returns:
            GroupBy object
        """
        if isinstance(by, str):
            by = [by]
        
        return GroupBy(self, by)
    
    # ==================== 4. Join ====================
    
    def join(self, other, left_on, right_on, how='inner'):
        """
        Join with another DataFrame
        
        parameters:
            other: DataFrame - the DataFrame to join with
            left_on: str - key column in the left DataFrame
            right_on: str - key column in the right DataFrame
            how: str - join type ('inner', 'left', 'right', 'outer')
        
        returns:
            DataFrame: join result
        """
        # Build index for right DataFrame
        right_index = {}
        for i, val in enumerate(other.data[right_on]):
            right_index.setdefault(val, []).append(i)
        
        # Initialize result container
        result_data = {col: [] for col in self.columns}
        for col in other.columns:
            if col != right_on:  # Avoid duplicate key columns
                result_data[f"{col}_right"] = []
        
        matched_right_indices = set()
        
        # Iterate through left DataFrame rows
        for i in range(self.row_count):
            left_key = self.data[left_on][i]
            
            if left_key in right_index:
                for right_i in right_index[left_key]:
                    matched_right_indices.add(right_i)
                    
                    # Add left columns
                    for col in self.columns:
                        result_data[col].append(self.data[col][i])
                    
                    # Add right columns
                    for col in other.columns:
                        if col != right_on:
                            result_data[f"{col}_right"].append(other.data[col][right_i])
            
            elif how in ['left', 'outer']:
                # Keep unmatched left rows
                for col in self.columns:
                    result_data[col].append(self.data[col][i])
                for col in other.columns:
                    if col != right_on:
                        result_data[f"{col}_right"].append(None)
        
        # Add unmatched right rows
        if how in ['right', 'outer']:
            for right_i in range(other.row_count):
                if right_i not in matched_right_indices:
                    for col in self.columns:
                        result_data[col].append(None)
                    for col in other.columns:
                        if col != right_on:
                            result_data[f"{col}_right"].append(other.data[col][right_i])
        
        return DataFrame(result_data)
    
    # ==================== Helper Methods ====================
    
    def head(self, n=5):
        """Return the first n rows"""
        return DataFrame({col: self.data[col][:n] for col in self.columns})
    
    def tail(self, n=5):
        """Return the last n rows"""
        return DataFrame({col: self.data[col][-n:] for col in self.columns})
    
    def shape(self):
        """Return (rows, columns)"""
        return (self.row_count, len(self.columns))
    
    def info(self):
        """Print DataFrame metadata"""
        print("DataFrame Info:")
        print(f"Rows: {self.row_count}")
        print(f"Columns: {len(self.columns)}\n")
        print("Column Names and Types:")
        for col in self.columns:
            sample_val = self.data[col][0] if self.row_count > 0 else None
            print(f"  {col}: {type(sample_val).__name__}")
    
    @classmethod
    def from_csv(cls, filepath, separator=",", quote_char='"'):
        """Create a DataFrame from a CSV file (loaded into memory)"""
        from io_module import load_csv_advanced
        data_dict = load_csv_advanced(filepath, separator, quote_char)
        if data_dict is None:
            raise ValueError(f"Failed to load CSV from {filepath}")
        return cls(data_dict)


# ==================== GroupBy Class ====================

class GroupBy:
    def __init__(self, dataframe, by):
        """
        GroupBy object representing grouped data
        """
        self.df = dataframe
        self.by = by
        self.groups = self._create_groups()
    
    def _create_groups(self):
        """Build grouping index"""
        groups = {}
        
        for i in range(self.df.row_count):
            key_values = tuple(self.df.data[col][i] for col in self.by)
            groups.setdefault(key_values, []).append(i)
        
        return groups
    
    def aggregate(self, agg_dict):
        """
        Perform aggregation
        
        parameters:
            agg_dict: dict - {column_name: aggregation_function}
                supported: 'sum', 'mean', 'max', 'min', 'count', 'std'
        
        returns:
            DataFrame
        """
        result_data = {col: [] for col in self.by}
        
        for col, func in agg_dict.items():
            result_data[f"{col}_{func}"] = []
        
        for key_values, indices in self.groups.items():
            # Add group keys
            for i, col in enumerate(self.by):
                result_data[col].append(key_values[i])
            
            # Compute aggregations
            for col, func_name in agg_dict.items():
                values = [self.df.data[col][i] for i in indices]
                values = [v for v in values if v is not None]
                
                if not values:
                    result = None
                else:
                    result = self._apply_aggregation(values, func_name)
                
                result_data[f"{col}_{func_name}"].append(result)
        
        return DataFrame(result_data)
    
    def _apply_aggregation(self, values, func_name):
        """Apply aggregation function"""
        if func_name == 'sum':
            return sum(values)
        elif func_name == 'mean':
            return sum(values) / len(values)
        elif func_name == 'max':
            return max(values)
        elif func_name == 'min':
            return min(values)
        elif func_name == 'count':
            return len(values)
        elif func_name == 'std':
            if len(values) < 1:
                return None
            mean = sum(values) / len(values)
            variance = sum((x - mean) ** 2 for x in values) / len(values)
            return variance ** 0.5
        else:
            raise ValueError(f"Unknown aggregation function: {func_name}")
    
    def size(self):
        """Return the size of each group"""
        result_data = {col: [] for col in self.by}
        result_data['size'] = []
        
        for key_values, indices in self.groups.items():
            for i, col in enumerate(self.by):
                result_data[col].append(key_values[i])
            result_data['size'].append(len(indices))

        return DataFrame(result_data)