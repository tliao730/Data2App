from core import DataFrame

class ChunkProcessor:
    """
    Utilities for applying operations on CSV chunks.
    Suitable for large datasets.
    """
    
    @staticmethod
    def filter_chunks(chunk_reader, condition):
        """
        Apply row filtering to each chunk
        """
        for chunk in chunk_reader:
            filtered = chunk.filter(condition)
            if len(filtered) > 0:
                yield filtered
    
    @staticmethod
    def aggregate_chunks(chunk_reader, group_by_cols, agg_dict):
        """
        Perform simplified chunk-based aggregation
        (Aggregations are merged at the end)
        """
        if isinstance(group_by_cols, str):
            group_by_cols = [group_by_cols]
        
        accumulated_groups = {}
        
        for chunk in chunk_reader:
            grouped = chunk.groupby(group_by_cols)
            chunk_result = grouped.aggregate(agg_dict)
            
            for i in range(len(chunk_result)):
                group_key = tuple(chunk_result.data[col][i] for col in group_by_cols)
                
                if group_key not in accumulated_groups:
                    accumulated_groups[group_key] = {}
                    for col in group_by_cols:
                        accumulated_groups[group_key][col] = chunk_result.data[col][i]
                    for agg_col in agg_dict.keys():
                        func = agg_dict[agg_col]
                        accumulated_groups[group_key][f"{agg_col}_{func}"] = []
                
                for agg_col in agg_dict.keys():
                    func = agg_dict[agg_col]
                    result_col = f"{agg_col}_{func}"
                    accumulated_groups[group_key][result_col].append(
                        chunk_result.data[result_col][i]
                    )
        
        final_data = {col: [] for col in group_by_cols}
        for agg_col in agg_dict.keys():
            func = agg_dict[agg_col]
            final_data[f"{agg_col}_{func}"] = []
        
        for group_key, group_data in accumulated_groups.items():
            for i, col in enumerate(group_by_cols):
                final_data[col].append(group_key[i])
            
            for agg_col in agg_dict.keys():
                func = agg_dict[agg_col]
                result_col = f"{agg_col}_{func}"
                values = [v for v in group_data[result_col] if v is not None]
                
                if not values:
                    final_value = None
                elif func == 'sum':
                    final_value = sum(values)
                elif func == 'max':
                    final_value = max(values)
                elif func == 'min':
                    final_value = min(values)
                elif func == 'count':
                    final_value = sum(values)
                elif func == 'mean':
                    final_value = sum(values) / len(values)
                else:
                    final_value = values[0]
                
                final_data[result_col].append(final_value)
        
        return DataFrame(final_data)
    
    @staticmethod
    def count_chunks(chunk_reader):
        """
        Count total number of rows across all chunks
        """
        total = 0
        for chunk in chunk_reader:
            total += len(chunk)
        return total
    
    @staticmethod
    def collect_chunks(chunk_reader, max_rows=None):
        """
        Combine all chunks into a single DataFrame
        (Use only if the full dataset fits into memory)
        """
        all_data = None
        total_rows = 0
        
        for chunk in chunk_reader:
            if all_data is None:
                all_data = {col: [] for col in chunk.columns}
            
            if max_rows and total_rows >= max_rows:
                break

            rows_to_add = len(chunk)
            if max_rows and total_rows + rows_to_add > max_rows:
                rows_to_add = max_rows - total_rows

            for col in chunk.columns:
                all_data[col].extend(chunk.data[col][:rows_to_add])
            
            total_rows += rows_to_add
        
        if all_data:
            return DataFrame(all_data)
        
        return DataFrame({})
