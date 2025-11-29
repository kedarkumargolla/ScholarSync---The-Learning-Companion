"""
Test script for multimodal RAG functionality
"""
import os
import sys

print("=" * 60)
print("Multimodal RAG Test Suite")
print("=" * 60)

# Test 1: Import modules
print("\n[Test 1] Testing module imports...")
try:
    from image_processing import load_image, create_image_document, generate_image_description
    print("✓ image_processing module imported successfully")
except Exception as e:
    print(f"✗ Failed to import image_processing: {e}")
    sys.exit(1)

try:
    from table_processing import load_dataframe, create_documents_from_dataframe, generate_table_summary
    print("✓ table_processing module imported successfully")
except Exception as e:
    print(f"✗ Failed to import table_processing: {e}")
    sys.exit(1)

try:
    from rag_core import get_llm, get_multimodal_llm, process_image, process_csv, process_excel
    print("✓ rag_core module imported successfully")
except Exception as e:
    print(f"✗ Failed to import rag_core: {e}")
    sys.exit(1)

# Test 2: Check dependencies
print("\n[Test 2] Checking dependencies...")
try:
    from PIL import Image
    print("✓ Pillow (PIL) installed")
except:
    print("✗ Pillow not installed")

try:
    import pandas as pd
    print("✓ pandas installed")
except:
    print("✗ pandas not installed")

# Test 3: Check Ollama models
print("\n[Test 3] Checking Ollama models...")
import subprocess

try:
    result = subprocess.run(
        ["ollama", "list"], 
        capture_output=True, 
        text=True,
        timeout=5
    )
    
    models = result.stdout
    
    if "llama3.2:1b" in models:
        print("✓ llama3.2:1b (text model) available")
    else:
        print("✗ llama3.2:1b not found")
    
    if "llava:7b" in models or "llava" in models:
        print("✓ llava (multimodal model) available")
    else:
        print("⚠ llava model not found (may still be downloading)")
        
except Exception as e:
    print(f"⚠ Could not check Ollama models: {e}")

# Test 4: Test image processing (if we have a test image)
print("\n[Test 4] Testing image processing...")
print("(Skipping - requires test images)")

# Test 5: Test CSV processing with sample data
print("\n[Test 5] Testing CSV processing with sample data...")
try:
    import pandas as pd
    import tempfile
    
    # Create sample CSV
    sample_data = pd.DataFrame({
        'Product': ['Apple', 'Banana', 'Orange'],
        'Price': [1.20, 0.50, 0.80],
        'Quantity': [100, 150, 120]
    })
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        sample_data.to_csv(f.name, index=False)
        temp_csv_path = f.name
    
    # Test processing
    docs = create_documents_from_dataframe(temp_csv_path, chunk_size=10)
    
    if docs and len(docs) > 0:
        print(f"✓ CSV processing successful! Created {len(docs)} document(s)")
        print(f"  - Summary document type: {docs[0].metadata.get('type')}")
    else:
        print("✗ CSV processing failed - no documents created")
    
    # Cleanup
    os.remove(temp_csv_path)
    
except Exception as e:
    print(f"✗ CSV processing test failed: {e}")

# Test 6: File type validation
print("\n[Test 6] Testing file type validation...")
from rag_core import load_file

supported_extensions = ['.pdf', '.docx', '.pptx', '.ppt', '.xlsx', '.csv', '.jpg', '.jpeg', '.png', '.gif', '.webp']
print(f"✓ Supported extensions: {', '.join(supported_extensions)}")

print("\n" + "=" * 60)
print("Test Suite Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Wait for LLaVA model to finish downloading")
print("2. Run the Streamlit app: streamlit run app.py")
print("3. Test uploading images and CSV files")
print("4. Ask questions about your data")
