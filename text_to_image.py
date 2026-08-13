import os
import json
import csv
from io import StringIO
from PIL import Image, ImageDraw, ImageFont

def text_to_optimized_images(text, output_width=2048, font_size=12, max_height=4000):
    """
    Renders text into a series of images, splitting into pages 
    to ensure we stay well under Anthropic's 8000px size limits.
    """
    try:
        font = ImageFont.truetype("Courier", font_size)
    except IOError:
        font = ImageFont.load_default()

    lines = []
    raw_lines = text.split('\n')
    max_char_width = output_width // (font_size * 0.6)
    
    # Wrap text lines
    for line in raw_lines:
        if len(line) == 0:
            lines.append("")
            continue
        while len(line) > max_char_width:
            lines.append(line[:int(max_char_width)])
            line = line[int(max_char_width):]
        lines.append(line)

    line_height = font_size + 4
    padding = 40
    
    # Calculate how many lines fit on a single image page
    lines_per_page = (max_height - padding) // line_height
    
    # Split lines into pages
    pages = [lines[i:i + lines_per_page] for i in range(0, len(lines), lines_per_page)]
    image_buffers = []

    for index, page_lines in enumerate(pages):
        output_height = len(page_lines) * line_height + padding
        
        # Create a clean, ultra-high-contrast 1-bit monochrome image canvas
        img = Image.new('1', (output_width, output_height), color=1)
        draw = ImageDraw.Draw(img)
        
        y_offset = 20
        for line in page_lines:
            draw.text((20, y_offset), line, font=font, fill=0)
            y_offset += line_height
            
        image_buffers.append(img)
        
    return image_buffers

def format_csv_to_table(raw_csv_text):
    f = StringIO(raw_csv_text.strip())
    reader = csv.reader(f)
    rows = list(reader)
    if not rows:
        return ""
    col_widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    table_lines = []
    for row in rows:
        aligned_row = [str(val).ljust(width) for val, width in zip(row, col_widths)]
        table_lines.append(" | ".join(aligned_row))
    return "\n".join(table_lines)

def process_file_content(file_path):
    _, ext = os.path.splitext(file_path.lower())
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()

    if not raw_content.strip():
        raise ValueError("File is empty.")

    if ext == ".json":
        parsed_json = json.loads(raw_content)
        return json.dumps(parsed_json, indent=2)
    elif ext == ".csv":
        return format_csv_to_table(raw_content)
    else:
        return raw_content

def main():
    supported_extensions = [".txt", ".json", ".csv"]
    target_file = None
    
    for file in os.listdir(os.getcwd()):
        # FIX: Added [1] to pull just the extension string from the split tuple
        ext = os.path.splitext(file)[1].lower()
        if file.lower().startswith("prompt") and ext in supported_extensions:
            target_file = file
            break

    if not target_file:
        print(f"Error: No prompt file found in {os.getcwd()}")
        return

    file_path = os.path.join(os.getcwd(), target_file)
    print(f"Found target file: {target_file}")

    try:
        formatted_text = process_file_content(file_path)
    except Exception as e:
        print(f"Error processing file: {e}")
        return

    print(f"Processed file data ({len(formatted_text)} characters). Splitting and rendering pages...")

    # Render into pages (each capped at 4000px height for safety)
    images = text_to_optimized_images(formatted_text, max_height=4000)

    # Save images locally
    for i, img in enumerate(images):
        output_name = f"output_page_{i + 1}.png"
        img.save(os.path.join(os.getcwd(), output_name), format="PNG")
        print(f"Saved: {output_name} ({img.width}x{img.height})")

    print(f"\nDone! Generated {len(images)} local image file(s).")

if __name__ == "__main__":
    main()
