#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 14:27:54 2026

@author: kweldon
"""

#!/usr/bin/env python3
import re
from pathlib import Path
from collections import defaultdict
from io import BytesIO
from PIL import Image
import cairosvg
import sys

def svg_to_pil(svg_path):
    """Renders complex SVGs to a PIL Image using Cairo."""
    png_data = cairosvg.svg2png(url=str(svg_path))
    return Image.open(BytesIO(png_data))

def get_bids_key(filename):
    """
    Extracts the identity of the file while ignoring the 'desc' part.
    Example: sub-01_run-1_desc-render_T1w.svg -> key: 'sub-01_run-1_T1w'
    """
    # Remove the desc- part and the extension to group files
    clean_name = re.sub(r'_desc-[^_+]+', '', filename).replace('.svg', '')
    return clean_name

def generate_output_name(original_name):
    """
    Replaces the specific desc- tag with 'desc-combined' and changes extension to .png
    """
    # Find '_desc-' followed by anything until the next '_' or '.'
    new_name = re.sub(r'_desc-[^_+.]+', '_desc-combined', original_name)
    return new_name.replace('.svg', '.png')

def main(folder):
    input_path = Path(folder)
    svg_files = list(input_path.glob("*.svg"))
    
    # Group files that are identical except for their desc- tag
    groups = defaultdict(list)
    for f in svg_files:
        key = get_bids_key(f.name)
        groups[key].append(f)

    for key, files in groups.items():
        if len(files) != 2:
            print(f"  Skipping {key}: Found {len(files)} files, need 2.")
            continue
        
        # Sort files so top/bottom order is predictable (alphabetical by desc)
        files.sort()
        
        # We use the first file as a template for the new name
        output_name = generate_output_name(files[0].name)
        output_path = input_path / output_name

        print(f"<¨ Stitching: {output_name}")
        
        try:
            img1 = svg_to_pil(files[0])
            img2 = svg_to_pil(files[1])

            # Vertical stack
            max_w = max(img1.width, img2.width)
            total_h = img1.height + img2.height
            
            combined = Image.new("RGBA", (max_w, total_h), (255, 255, 255, 0))
            combined.paste(img1, (0, 0))
            combined.paste(img2, (0, img1.height))

            combined.save(output_path)
            print(f" Saved to: {output_path.name}")
            
        except Exception as e:
            print(f"L Error processing {key}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python stitch_bids.py <folder_path>")
    else:
        main(sys.argv[1])
        

# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM, drawSize
# from reportlab.graphics.shapes import Drawing

# # Load the SVGs
# drawing1 = svg2rlg("top.svg")
# drawing2 = svg2rlg("bottom.svg")

# # Create a new blank canvas
# combined = Drawing(max(drawing1.width, drawing2.width), drawing1.height + drawing2.height)

# # Add the first image at the top
# combined.add(drawing1)

# # Shift the second image down and add it
# drawing2.translate(0, -drawing1.height) # Coordinates start from bottom-left in ReportLab
# combined.add(drawing2)

# # Save as PNG
# renderPM.drawToFile(combined, "final_output.png", fmt="PNG")

#!/usr/bin/env python3