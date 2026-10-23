#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 13:49:00 2025

@author: kweldon
"""

#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import sys
import re
from collections import defaultdict

def make_grid(image_paths, output_path, grid_size=(3,3)):
    imgs = [Image.open(p) for p in image_paths]
    w, h = imgs[0].size
    grid_img = Image.new("RGB", (grid_size[0]*w, grid_size[1]*h), color="white")

    for idx, img in enumerate(imgs):
        row, col = divmod(idx, grid_size[0])
        # Ensure images are the same size as the first image
        if img.size != (w, h):
            img = img.resize((w, h), Image.Resampling.LANCZOS)
        grid_img.paste(img, (col*w, row*h))
    
    grid_img.save(output_path)
    print(f" Saved grid: {output_path.name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python make_grid.py <image_folder>")
        sys.exit(1)

    image_dir = Path(sys.argv[1])
    png_files = list(image_dir.glob("*.png"))
    
    # 1. Group files by Subject ID
    # This finds 'sub-XXXX' and creates a dictionary of files belonging to them
    sub_groups = defaultdict(list)
    for f in png_files:
        match = re.search(r'(sub-[a-zA-Z0-9]+)', f.name)
        if match:
            sub_groups[match.group(1)].append(f)

    search_terms = [
        "desc-AxialSuperiorFrontal_T1w",
        "desc-AxialBasalGangliaPutamen_T1w",
        "desc-AxialInferiorTemporalCerebellum_T1w",
        "desc-CoronalOrbitoFrontal_T1w",
        "desc-CoronalCaudateAmygdala_T1w",
        "desc-CoronalPosteriorParietalLingual_T1w",
        "desc-SagittalInsulaFrontoTemporal_T1w",
        "desc-SagittalCorpusCallosum_T1w",
        "desc-SagittalInsulaTemporalHippocampalSulcus_T1w",
    ]

    # 2. Iterate through each subject group
    for sub_id, files in sub_groups.items():
        selected_images = []
        template_filename = None

        for term in search_terms:
            matches = [p for p in files if term in p.name]
            if matches:
                selected_images.append(matches[0])
                if template_filename is None:
                    template_filename = matches[0].name
            else:
                # Create a blank if this specific slice is missing for THIS subject
                ref_img = Image.open(files[0])
                blank = Image.new("RGB", ref_img.size, color="white")
                blank_path = image_dir / f"TEMP_blank_{sub_id}_{term}.png"
                blank.save(blank_path)
                selected_images.append(blank_path)

        # 3. Handle the 'desc-combined' naming for this subject
        if template_filename:
            output_name = re.sub(r'_desc-[^_+.]+', '_desc-combined', template_filename)
            output_path = image_dir / output_name
            
            make_grid(selected_images, output_path)
            
            # Clean up temp blank files
            for p in selected_images:
                if "TEMP_blank_" in str(p):
                    p.unlink()

if __name__ == "__main__":
    main()
