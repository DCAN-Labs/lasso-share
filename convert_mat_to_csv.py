#!/usr/bin/env python3
"""
Author: rae McCollum w Claude 2 July 26
Purpose: Convert the surface area mat files into csv format
Usage: python mat_to_csv.py /path/to/template_matching_directory
"""

from pathlib import Path
from scipy.io import loadmat
import argparse
import csv

NETWORK_NAMES = [
    "Default Mode",
    "Visual",
    "Frontoparietal",
    "None",
    "Dorsal Attention",
    "None",
    "Ventral Attention",
    "Salience",
    "Cingulo-Opercular",
    "Sensorimotor Medial",
    "Sensorimotor Lateral",
    "Auditory",
    "Temporal Pole",
    "Medial Temporal Lobe",
    "Parietal Medial",
    "Partieto-Occipital",
    "None",
    "SCAN",
]


def convert_mat_to_csv(mat_path: Path, network_names: list[str]) -> Path:
    """Load a .mat file and write its network_surfarea data to a CSV."""
    mat = loadmat(mat_path)

    if "network_surfarea" not in mat:
        raise KeyError(f"'network_surfarea' not found in {mat_path.name}")

    values = mat["network_surfarea"].squeeze().tolist()

    # squeeze().tolist() can return a scalar if there's only 1 value;
    # make sure we always have a list.
    if not isinstance(values, list):
        values = [values]

    if len(values) != len(network_names):
        raise ValueError(
            f"{mat_path.name}: expected {len(network_names)} values, "
            f"got {len(values)}"
        )

    csv_path = mat_path.with_suffix(".csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["network", "surface_area"])
        writer.writerows(zip(network_names, values))

    return csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert sub-*/*_surface_area.mat files to CSV."
    )
    parser.add_argument(
        "directory",
        type=Path,
        help="Parent directory containing sub-* folders",
    )
    args = parser.parse_args()

    parent_dir = args.directory
    if not parent_dir.is_dir():
        raise SystemExit(f"Not a directory: {parent_dir}")

    sub_dirs = sorted(p for p in parent_dir.iterdir() if p.is_dir() and p.name.startswith("sub-"))

    if not sub_dirs:
        print(f"No 'sub-*' folders found in {parent_dir}")
        return

    n_converted = 0
    n_skipped = 0

    for sub_dir in sub_dirs:
        mat_files = sorted(sub_dir.glob("*_surface_area.mat"))

        if not mat_files:
            print(f"[skip] No surface_area.mat file found in {sub_dir.name}")
            n_skipped += 1
            continue

        for mat_path in mat_files:
            try:
                csv_path = convert_mat_to_csv(mat_path, NETWORK_NAMES)
                print(f"[ok]   {mat_path.name} -> {csv_path.name}")
                n_converted += 1
            except (KeyError, ValueError) as e:
                print(f"[error] {mat_path.name}: {e}")
                n_skipped += 1

    print(f"\nDone. Converted: {n_converted}, Skipped/errored: {n_skipped}")


if __name__ == "__main__":
    main()
