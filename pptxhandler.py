import re
from hashlib import md5

def get_slide_shapes(slide):
    """Returns a list of (shape_id, fingerprint) for elements with text."""                
    contents = []
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            contents.append((shape.shape_id, fingerprint(shape.text.strip())))
    return contents

def fingerprint(text):
    return(md5(text.encode()).hexdigest())

def markdown_to_shape(shape, markdown_text):
    """Parses Markdown and applies it to a PowerPoint shape."""
    if not shape.has_text_frame:
        return

    text_frame = shape.text_frame
    text_frame.clear() # Wipe existing content
    
    lines = markdown_text.split('\n')
    
    for i, line in enumerate(lines):
        # Create a new paragraph (except for the first one which is created by default)
        p = text_frame.paragraphs[0] if i == 0 else text_frame.add_paragraph()
        
        # Detect bullet level (counting leading spaces)
        strip_line = line.lstrip()
        if strip_line.startswith('* '):
            p.level = (len(line) - len(strip_line)) // 2
            content = strip_line[2:]
        else:
            content = line

        # Regex to find [text](url), **bold**, and *italic*
        # This is a simplified parser; order of bold/italic matters
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))', content)
        
        for part in parts:
            if not part: continue
            
            run = p.add_run()
            
            if part.startswith('**') and part.endswith('**'):
                run.text = part[2:-2]
                run.font.bold = True
            elif part.startswith('*') and part.endswith('*'):
                run.text = part[1:-1]
                run.font.italic = True
            elif part.startswith('[') and '(' in part:
                # Basic Markdown Link: [text](url)
                link_text = re.search(r'\[(.*?)\]', part).group(1)
                link_url = re.search(r'\((.*?)\)', part).group(1)
                run.text = link_text
                run.hyperlink.address = link_url
            else:
                run.text = part


def get_shape_markdown(shape):
    """Converts a PowerPoint shape's text and formatting to Markdown."""
    if not shape.has_text_frame:
        return ""
    
    md_paragraphs = []
    for paragraph in shape.text_frame.paragraphs:
        md_runs = ""
        for run in paragraph.runs:
            text = run.text
            if not text: continue
            
            # Apply formatting markers
            if run.font.bold:
                text = f"**{text}**"
            if run.font.italic:
                text = f"*{text}*"
            
            # Handle Hyperlinks
            if run.hyperlink.address:
                text = f"[{text}]({run.hyperlink.address})"
            
            md_runs += text
        
        # Handle Bullet Levels (Basic)
        prefix = ""
        if paragraph.level > 0:
            prefix = "  " * paragraph.level + "* "
        md_paragraphs.append(prefix + md_runs)        
    return "\n".join(md_paragraphs)
