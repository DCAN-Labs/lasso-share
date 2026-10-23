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

def make_grid(image_paths, output_path="grid.png", grid_size=(3,3)):
    if len(image_paths) != grid_size[0] * grid_size[1]:
        sys.exit(f"L Expected {grid_size[0]*grid_size[1]} images, got {len(image_paths)}.")

    imgs = [Image.open(p) for p in image_paths]
    w, h = imgs[0].size
    grid_img = Image.new("RGB", (grid_size[0]*w, grid_size[1]*h), color="white")

    for idx, img in enumerate(imgs):
        row, col = divmod(idx, grid_size[0])
        grid_img.paste(img, (col*w, row*h))
    grid_img.save(output_path)
    print(f" Saved grid to: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python make_grid_by_keywords.py <image_folder> [output.png]")
        sys.exit(1)

    image_dir = Path(sys.argv[1])
    if not image_dir.is_dir():
        sys.exit("L The input path must be a directory containing PNGs.")

    output_name = sys.argv[2] if len(sys.argv) > 2 else "grid.png"

    # >é Define the search strings in order
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

    png_files = list(image_dir.glob("*.png"))
    if not png_files:
        sys.exit("L No PNG files found.")

    selected_images = []
    for term in search_terms:
        matches = [p for p in png_files if term in p.name]
        if matches:
            selected_images.append(matches[0])
        else:
            print(f"  No match found for '{term}'  leaving blank.")
            blank = Image.new("RGB", (png_files[0].width, png_files[0].height), color="white")
            blank_path = image_dir / f"blank_{term}.png"
            blank.save(blank_path)
            selected_images.append(blank_path)

    make_grid(selected_images, output_name)

if __name__ == "__main__":
    main()
