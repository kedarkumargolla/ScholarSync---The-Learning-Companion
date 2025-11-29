import os
import pandas as pd
from langchain_core.documents import Document
from typing import List

def load_dataframe(file_path):
    """Load CSV or XLSX file as a pandas DataFrame"""
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.csv':
            return pd.read_csv(file_path)
        elif ext in ['.xlsx', '.xls']:
            # Read first sheet by default
            return pd.read_excel(file_path, sheet_name=0)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    except Exception as e:
        raise ValueError(f"Error loading {file_path}: {str(e)}")

def generate_table_summary(df, filename=""):
    """Generate a natural language summary of the DataFrame"""
    summary_parts = []
    
    # Basic info
    summary_parts.append(f"Table: {filename}")
    summary_parts.append(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Column information
    summary_parts.append(f"\nColumns: {', '.join(df.columns.tolist())}")
    
    # Data types
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()
    
    if numeric_cols:
        summary_parts.append(f"Numeric columns: {', '.join(numeric_cols)}")
    if text_cols:
        summary_parts.append(f"Text columns: {', '.join(text_cols)}")
    
    # Basic statistics for numeric columns
    if numeric_cols:
        summary_parts.append("\nNumeric Statistics:")
        for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            stats = df[col].describe()
            summary_parts.append(
                f"  {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, "
                f"mean={stats['mean']:.2f}, median={stats['50%']:.2f}"
            )
    
    # Sample values for text columns
    if text_cols:
        summary_parts.append("\nSample Values:")
        for col in text_cols[:3]:  # Limit to first 3 text columns
            unique_vals = df[col].dropna().unique()[:5]
            summary_parts.append(f"  {col}: {', '.join(map(str, unique_vals))}")
    
    return "\n".join(summary_parts)

def extract_column_metadata(df):
    """Extract schema information for better retrieval"""
    metadata = {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "row_count": len(df),
        "column_count": len(df.columns),
        "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
        "text_columns": df.select_dtypes(include=['object']).columns.tolist()
    }
    return metadata

def chunk_dataframe(df, chunk_size=100, filename=""):
    """
    Smart chunking that preserves context.
    Each chunk includes column headers and a subset of rows.
    """
    chunks = []
    total_rows = len(df)
    
    # Always include column information in metadata
    column_info = f"Columns: {', '.join(df.columns.tolist())}"
    
    for start_idx in range(0, total_rows, chunk_size):
        end_idx = min(start_idx + chunk_size, total_rows)
        chunk_df = df.iloc[start_idx:end_idx]
        
        # Convert chunk to a readable string format
        chunk_text = f"Table: {filename}\n"
        chunk_text += f"{column_info}\n"
        chunk_text += f"Rows {start_idx + 1} to {end_idx}:\n\n"
        chunk_text += chunk_df.to_string(index=False)
        
        # Add summary statistics for this chunk if it has numeric data
        numeric_cols = chunk_df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            chunk_text += f"\n\nChunk Statistics:\n"
            for col in numeric_cols:
                chunk_text += f"  {col}: min={chunk_df[col].min()}, max={chunk_df[col].max()}, mean={chunk_df[col].mean():.2f}\n"
        
        chunks.append(chunk_text)
    
    return chunks

def create_documents_from_dataframe(file_path, chunk_size=100) -> List[Document]:
    """
    Create Document objects from a CSV/XLSX file with enhanced processing.
    Returns both a summary document and chunked data documents.
    """
    filename = os.path.basename(file_path)
    
    try:
        # Load the dataframe
        df = load_dataframe(file_path)
        
        # Extract metadata
        col_metadata = extract_column_metadata(df)
        
        # Create summary document
        summary_text = generate_table_summary(df, filename)
        summary_doc = Document(
            page_content=summary_text,
            metadata={
                "source": file_path,
                "filename": filename,
                "type": "table_summary",
                "extension": os.path.splitext(filename)[1].lower(),
                "columns": ", ".join(col_metadata["columns"]),
                "row_count": col_metadata["row_count"],
                "column_count": col_metadata["column_count"],
                "numeric_columns": ", ".join(col_metadata["numeric_columns"]),
                "text_columns": ", ".join(col_metadata["text_columns"])
            }
        )
        
        # Create chunked documents
        chunks = chunk_dataframe(df, chunk_size, filename)
        chunk_docs = []
        
        for i, chunk_text in enumerate(chunks):
            chunk_doc = Document(
                page_content=chunk_text,
                metadata={
                    "source": file_path,
                    "filename": filename,
                    "type": "table_chunk",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "extension": os.path.splitext(filename)[1].lower(),
                    "columns": ", ".join(col_metadata["columns"])
                }
            )
            chunk_docs.append(chunk_doc)
        
        # Return summary + all chunks
        return [summary_doc] + chunk_docs
        
    except Exception as e:
        raise ValueError(f"Error processing {file_path}: {str(e)}")

def query_dataframe(df, query_text):
    """
    Simple query interface for pandas DataFrames.
    Supports basic filtering and aggregation.
    """
    # This is a placeholder for future pandas query capabilities
    # Could be extended with natural language to pandas query translation
    return df.to_string()
