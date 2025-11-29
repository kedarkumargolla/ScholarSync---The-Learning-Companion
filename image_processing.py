import os
import base64
from PIL import Image
from io import BytesIO
from langchain_core.documents import Document

def load_image(file_path):
    """Load and validate an image file"""
    try:
        img = Image.open(file_path)
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        return img
    except Exception as e:
        raise ValueError(f"Error loading image {file_path}: {str(e)}")

def image_to_base64(file_path):
    """Convert image to base64 string for embedding"""
    try:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error encoding image {file_path}: {str(e)}")

def generate_image_description(image_path, llm):
    """Use multimodal LLM to generate a description of the image"""
    try:
        # For LLaVA, we need to use a specific format
        # The LLM will be called with the image path directly
        prompt = """Describe this image in detail. Include:
1. Main subjects or objects
2. Colors and visual style
3. Text content (if any)
4. Overall purpose or context

Keep the description factual and comprehensive."""
        
        # LLaVA accepts image paths directly in Ollama
        response = llm.invoke(prompt, images=[image_path])
        
        if hasattr(response, 'content'):
            return response.content
        return str(response)
        
    except Exception as e:
        raise ValueError(f"Error generating description for {image_path}: {str(e)}")

def create_image_document(file_path, description=None):
    """Create a Document object from an image file"""
    filename = os.path.basename(file_path)
    
    # Metadata for the image
    metadata = {
        "source": file_path,
        "filename": filename,
        "type": "image",
        "extension": os.path.splitext(filename)[1].lower()
    }
    
    # If we have a description, use it as the page_content
    # Otherwise, just use the filename and path
    if description:
        content = f"Image: {filename}\n\nDescription: {description}"
    else:
        content = f"Image file: {filename}\nLocation: {file_path}"
    
    return Document(
        page_content=content,
        metadata=metadata
    )

def create_image_chunks(image_docs):
    """
    Create searchable chunks from image documents.
    For images, we typically don't need to split - each image is its own chunk.
    """
    # Images don't need chunking like text documents
    # Each image description is already a manageable size
    return image_docs

def get_image_info(file_path):
    """Get basic information about an image"""
    try:
        img = load_image(file_path)
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format,
            "mode": img.mode,
            "size_bytes": os.path.getsize(file_path)
        }
    except Exception as e:
        return {"error": str(e)}
