#!/usr/bin/env python
"""
Convert PRD.md to PDF via HTML using markdown2 and weasyprint
"""
import markdown2
import os

def markdown_to_pdf_html(md_file, pdf_file):
    """Convert markdown to PDF via HTML"""
    
    # Read markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"Converting {md_file} to HTML...")
    
    # Convert markdown to HTML with extras
    html_content = markdown2.markdown(
        md_content,
        extras=[
            'tables',
            'fenced-code-blocks',
            'header-ids',
            'toc',
            'code-friendly',
            'break-on-newline'
        ]
    )
    
    # Create full HTML document with styling
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Product Requirements Document - Learning Companion Multimodal RAG</title>
    <style>
        @page {{
            size: A4;
            margin: 1in;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-before: always;
        }}
        h1:first-of-type {{
            page-break-before: avoid;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 25px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
        }}
        h4, h5, h6 {{
            color: #95a5a6;
            margin-top: 15px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid #3498db;
            padding-left: 20px;
            margin-left: 0;
            font-style: italic;
            color: #666;
        }}
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        li {{
            margin: 8px 0;
        }}
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        a {{
            color: #3498db;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .page-break {{
            page-break-after: always;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    # Save HTML file
    html_file = pdf_file.replace('.pdf', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ Created {html_file}")
    
    # Try to convert to PDF using weasyprint
    try:
        from weasyprint import HTML
        print(f"Converting HTML to PDF...")
        HTML(html_file).write_pdf(pdf_file)
        print(f"✅ Successfully created {pdf_file}")
        
        # Clean up HTML file
        # os.remove(html_file)
        
        return True
    except ImportError:
        print(f"⚠️  weasyprint not installed.")
        print(f"   Created {html_file} instead.")
        print(f"\nTo create PDF:")
        print(f"   Option 1: Open {html_file} in browser and print to PDF")
        print(f"   Option 2: Install weasyprint: pip install weasyprint")
        print(f"   Option 3: Use PRD.docx to export as PDF from Word")
        return False
    except Exception as e:
        print(f"⚠️  PDF creation failed: {e}")
        print(f"   Created {html_file} instead.")
        print(f"   You can open this in a browser and print to PDF.")
        return False

if __name__ == "__main__":
    input_file = "PRD.md"
    output_file = "PRD.pdf"
    
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        exit(1)
    
    try:
        success = markdown_to_pdf_html(input_file, output_file)
        
        print(f"\n✨ Conversion complete!")
        print(f"\n📄 Files created:")
        
        if os.path.exists("PRD.docx"):
            size_kb = os.path.getsize("PRD.docx") / 1024
            print(f"   ✅ PRD.docx ({size_kb:.1f} KB)")
        
        if os.path.exists("PRD.pdf"):
            size_kb = os.path.getsize("PRD.pdf") / 1024
            print(f"   ✅ PRD.pdf ({size_kb:.1f} KB)")
        
        html_file = "PRD.html"
        if os.path.exists(html_file):
            size_kb = os.path.getsize(html_file) / 1024
            print(f"   ✅ PRD.html ({size_kb:.1f} KB)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
