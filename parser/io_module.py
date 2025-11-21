from utils import parse_csv_line, _attempt_convert_type
from core import DataFrame  

def load_csv_advanced(filePath, separator=",", quote_char='"'):
    """
    Advanced CSV loader that properly handles quoted fields
    Example: "Smith, John",25,USA
    Loads the entire file into memory.
    """
    data_dict = {}
    header = []
    
    try:
        with open(filePath, "r", encoding="utf-8") as f:
            # Read header row
            header_line = f.readline().strip()
            header = parse_csv_line(header_line, separator, quote_char)
            header = [col.strip().strip(quote_char) for col in header]
            
            data_dict = {col_name: [] for col_name in header}
            
            # Read data rows
            for line_number, line in enumerate(f, start=2):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue
                
                values = parse_csv_line(cleaned_line, separator, quote_char)
                
                if len(values) == len(header):
                    for i, col_name in enumerate(header):
                        converted_value = _attempt_convert_type(values[i])
                        data_dict[col_name].append(converted_value)
                else:
                    print(f"Warning: Line {line_number} column mismatch (Expected {len(header)}, got {len(values)})")
        
        return data_dict
        
    except FileNotFoundError:
        print(f"Error: File not found at {filePath}")
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        import traceback
        traceback.print_exc()
        return None
    

class CSVChunkReader:
    """
    Chunk-based CSV reader.
    Reads large CSV files in small batches (memory-efficient).
    Returns each chunk as a DataFrame.
    """
    
    def __init__(self, filepath, separator=",", quote_char='"', chunk_size=1000):
        """
        Initialize chunk reader
        
        parameters:
            filepath: str - path to the CSV file
            separator: str - field separator
            quote_char: str - quote character
            chunk_size: int - number of rows per chunk
        """
        self.filepath = filepath
        self.separator = separator
        self.quote_char = quote_char
        self.chunk_size = chunk_size
        self.header = None
        self.total_rows_read = 0
    
    def __iter__(self):
        return self.read_chunks()
    
    def read_chunks(self):
        """
        Generator that yields DataFrame chunks
        
        Yields:
            DataFrame - batch of rows
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                header_line = f.readline().strip()
                if not header_line:
                    raise ValueError("File is empty")
                
                self.header = parse_csv_line(header_line, self.separator, self.quote_char)
                self.header = [col.strip().strip(self.quote_char) for col in self.header]
                
                chunk_data = {col: [] for col in self.header}
                chunk_row_count = 0
                
                for line_number, line in enumerate(f, start=2):
                    cleaned_line = line.strip()
                    if not cleaned_line:
                        continue
                    
                    values = parse_csv_line(cleaned_line, self.separator, self.quote_char)
                    
                    if len(values) == len(self.header):
                        for i, col in enumerate(self.header):
                            converted_value = _attempt_convert_type(values[i])
                            chunk_data[col].append(converted_value)
                        
                        chunk_row_count += 1
                        self.total_rows_read += 1
                        
                        if chunk_row_count >= self.chunk_size:
                            yield DataFrame(chunk_data)
                            chunk_data = {col: [] for col in self.header}
                            chunk_row_count = 0
                    else:
                        print(f"Warning: Line {line_number} column mismatch (Expected {len(self.header)}, got {len(values)})")
                
                if chunk_row_count > 0:
                    yield DataFrame(chunk_data)
        
        except FileNotFoundError:
            print(f"Error: File not found at {self.filepath}")
            return
        except Exception as e:
            print(f"Error reading CSV chunks: {e}")
            import traceback
            traceback.print_exc()
            return


def read_csv_chunks(filepath, separator=",", quote_char='"', chunk_size=1000):
    """
    Convenience function: chunked CSV reader
    
    Example:
        for chunk in read_csv_chunks("large.csv", chunk_size=1000):
            print(chunk.shape())
    """
    return CSVChunkReader(filepath, separator, quote_char, chunk_size)


