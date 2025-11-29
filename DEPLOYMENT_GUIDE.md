# Local Deployment Guide - Learning Companion Multimodal RAG

This guide provides step-by-step instructions to deploy the Learning Companion Multimodal RAG application on your local Windows machine.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)
7. [Usage Guide](#usage-guide)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### 1. Python 3.9 or higher
- Download from: https://www.python.org/downloads/
- During installation, **check the box** to "Add Python to PATH"
- Verify installation:
  ```powershell
  python --version
  ```

### 2. Ollama (Local LLM Runtime)
- Download from: https://ollama.ai/download
- Install the Windows version
- Verify installation:
  ```powershell
  ollama --version
  ```

### 3. Git (Optional, for cloning)
- Download from: https://git-scm.com/download/win
- Verify installation:
  ```powershell
  git --version
  ```

---

## System Requirements

- **OS**: Windows 10/11
- **RAM**: Minimum 8GB (16GB+ recommended for better performance)
- **Storage**: At least 10GB free space (for models and data)
- **GPU**: Optional (NVIDIA GPU with CUDA support improves performance)

---

## Installation Steps

### Step 1: Pull Required Ollama Models

Open PowerShell or Command Prompt and run the following commands to download the necessary AI models:

```powershell
# Text-only model for chat responses (smaller, faster)
ollama pull llama3.2:1b

# Vision-capable model for image processing
ollama pull llava:7b

# Embedding model for RAG (Retrieval-Augmented Generation)
ollama pull nomic-embed-text
```

> **Note**: These downloads may take several minutes depending on your internet speed. The models are:
> - `llama3.2:1b` - ~1.3GB
> - `llava:7b` - ~4.7GB
> - `nomic-embed-text` - ~274MB

### Step 2: Verify Ollama Models

List all installed models to confirm:

```powershell
ollama list
```

You should see all three models listed.

### Step 3: Navigate to Project Directory

Open PowerShell and navigate to the project folder:

```powershell
cd "d:\AI\Learning Companion Multimodal"
```

### Step 4: Create Virtual Environment

Create a Python virtual environment to isolate dependencies:

```powershell
python -m venv .venv
```

### Step 5: Activate Virtual Environment

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

> **Troubleshooting**: If you get an execution policy error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

You should see `(.venv)` prefix in your terminal prompt when activated.

### Step 6: Upgrade pip

Ensure you have the latest version of pip:

```powershell
python -m pip install --upgrade pip
```

### Step 7: Install Python Dependencies

Install all required packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

Packages being installed:
- `streamlit` - Web UI framework
- `langchain` - LLM orchestration framework
- `langchain-community` - Community integrations
- `langchain-ollama` - Ollama integration
- `langchain-chroma` - Vector database integration
- `chromadb` - Vector database
- `pypdf` - PDF processing
- `python-docx` - DOCX processing
- `openpyxl` - Excel processing
- `python-pptx` - PowerPoint processing
- `Pillow` - Image processing
- `pandas` - Data manipulation
- `tabulate` - Table formatting
- `unstructured` - Advanced document parsing

---

## Configuration

### Optional: Modify Model Settings

If you want to use different Ollama models, edit `rag_core.py`:

```python
# Lines 18-20
MODEL_NAME = "llama3.2:1b"        # Text-only model
MULTIMODAL_MODEL = "llava:7b"     # Vision-capable model
EMBEDDING_MODEL = "nomic-embed-text"  # Embedding model
```

You can replace these with any compatible Ollama models.

### Optional: Adjust Chunk Size

For different chunking behavior, modify line 194 in `rag_core.py`:

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
```

- `chunk_size`: Maximum characters per chunk (default: 1000)
- `chunk_overlap`: Overlap between chunks for context continuity (default: 200)

---

## Running the Application

### Step 1: Ensure Ollama is Running

Ollama should start automatically after installation. Verify it's running:

```powershell
ollama serve
```

If it's already running, you'll see a message indicating the server is active. You can press `Ctrl+C` to exit or open a new terminal for the next step.

### Step 2: Start the Streamlit Application

In a new terminal (or the same one if Ollama is running in background), activate the virtual environment and run:

```powershell
cd "d:\AI\Learning Companion Multimodal"
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Step 3: Access the Application

The application will automatically open in your default browser at:

```
http://localhost:8501
```

If it doesn't open automatically, manually navigate to that URL.

---

## Troubleshooting

### Issue 1: Virtual Environment Not Activating

**Error**: PowerShell execution policy prevents script execution.

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Issue 2: Ollama Connection Error

**Error**: `Connection refused` or `Ollama not found`

**Solutions**:
1. Verify Ollama is installed:
   ```powershell
   ollama --version
   ```

2. Start Ollama service:
   ```powershell
   ollama serve
   ```

3. Check if models are available:
   ```powershell
   ollama list
   ```

---

### Issue 3: Model Not Found

**Error**: `Model 'llama3.2:1b' not found`

**Solution**: Pull the missing model:
```powershell
ollama pull llama3.2:1b
```

---

### Issue 4: Import Errors

**Error**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

### Issue 5: Port Already in Use

**Error**: `Port 8501 is already in use`

**Solution**: Either:
1. Kill the existing process using that port, or
2. Run Streamlit on a different port:
   ```powershell
   streamlit run app.py --server.port 8502
   ```

---

### Issue 6: ChromaDB Permission Error

**Error**: Permission denied when accessing `chroma_db` folder

**Solution**:
1. Close the application
2. Delete the `chroma_db` folder:
   ```powershell
   Remove-Item -Recurse -Force chroma_db
   ```
3. Restart the application

---

### Issue 7: Out of Memory

**Error**: System runs out of memory during processing

**Solutions**:
1. Use a smaller model (e.g., `llama3.2:1b` instead of larger variants)
2. Process fewer files at once
3. Reduce chunk size in `rag_core.py`
4. Close other memory-intensive applications

---

## Usage Guide

### 1. Knowledge Base Management (Tab 1)

#### Creating Folders
1. Open sidebar → **Folder Actions**
2. Select **Create Subfolder**
3. Choose parent folder
4. Enter folder name → Click **Create Folder**

#### Uploading Files

**Single File Upload**:
1. Select target folder in sidebar
2. Choose **Single File Upload**
3. Click **Browse files**
4. Select one file → Click **Process Files**

**Batch Upload**:
1. Select target folder in sidebar
2. Choose **Batch File Upload**
3. Select multiple files or a ZIP archive
4. Click **Process Files**

**Supported File Types**:
- Documents: PDF, DOCX, PPTX, PPT
- Data: XLSX, CSV
- Images: JPG, JPEG, PNG, GIF, WEBP
- Archives: ZIP (for batch upload)

#### Deleting Folders
1. Open sidebar → **Folder Actions**
2. Select **Delete Folder**
3. Choose folder to delete
4. Click **Delete Folder**

### 2. Chat with Knowledge Base (Tab 2)

#### Quick File Upload
1. Click **Browse files** under **Quick Upload**
2. Select a file
3. Click **Add to Context**

#### Asking Questions
1. Type your question in the chat input at the bottom
2. Press Enter or click Send
3. View the AI response and source documents

#### Viewing Sources
Click **📚 Source Documents** to see:
- Document names
- Content excerpts
- Images (if applicable)

### 3. Reset Everything

> **⚠️ WARNING**: This permanently deletes all data!

To reset the entire knowledge base:
1. Open sidebar → **System Settings**
2. Check the confirmation box
3. Click **🗑️ Reset Everything**
4. Refresh the page

---

## Advanced Configuration

### Custom Embeddings

To use a different embedding model, modify `rag_core.py`:

```python
EMBEDDING_MODEL = "your-embedding-model"  # Line 20
```

Then pull the model:
```powershell
ollama pull your-embedding-model
```

### Retrieval Parameters

Adjust the number of retrieved documents in `rag_core.py` (line 230):

```python
retriever = vectorstore.as_retriever(
    search_type="similarity", 
    search_kwargs={"k": 4}  # Change this number
)
```

### Custom Prompts

Modify the system prompt in `rag_core.py` (lines 234-242):

```python
template = """Your custom prompt here...
    
Context: {context}
    
Question: {question}
    
Helpful Answer:"""
```

---

## Stopping the Application

To stop the application:

1. **Stop Streamlit**: Press `Ctrl+C` in the terminal running Streamlit
2. **Deactivate Virtual Environment**:
   ```powershell
   deactivate
   ```
3. **Stop Ollama** (optional):
   - Close the Ollama application from the system tray, or
   - Press `Ctrl+C` in the terminal running `ollama serve`

---

## Directory Structure

After setup, your project should look like this:

```
d:\AI\Learning Companion Multimodal\
├── .venv\                          # Virtual environment
├── __pycache__\                    # Python cache files
├── chroma_db\                      # Vector database (auto-created)
├── knowledge_base\                 # Uploaded files (auto-created)
│   └── Others\                     # Default folder
├── app.py                          # Main Streamlit application
├── rag_core.py                     # RAG logic
├── image_processing.py             # Image handling
├── table_processing.py             # Table/Excel handling
├── test_multimodal.py              # Test suite
├── requirements.txt                # Python dependencies
├── DEPLOYMENT_GUIDE.md            # This file
└── transcript about how to build local RAG.txt
```

---

## Next Steps

1. **Test the Installation**: Upload a sample PDF and ask questions about it
2. **Organize Your Knowledge Base**: Create folders for different subjects/topics
3. **Explore Features**: Try uploading images, Excel files, and PowerPoint presentations
4. **Run Tests**: Execute the test suite to verify everything works:
   ```powershell
   python test_multimodal.py
   ```

---

## Support & Resources

- **Ollama Documentation**: https://ollama.ai/docs
- **LangChain Documentation**: https://python.langchain.com/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **ChromaDB Documentation**: https://docs.trychroma.com/

---

## Updates & Maintenance

### Updating Dependencies

To update all packages to their latest versions:

```powershell
pip install --upgrade -r requirements.txt
```

### Updating Ollama Models

To update Ollama models to the latest versions:

```powershell
ollama pull llama3.2:1b
ollama pull llava:7b
ollama pull nomic-embed-text
```

---

## License & Credits

This application uses:
- **Streamlit** for the web interface
- **LangChain** for LLM orchestration
- **Ollama** for local LLM inference
- **ChromaDB** for vector storage

---

**Happy Learning! 📚✨**
