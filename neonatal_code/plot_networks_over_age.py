"""
plot_surfacearea_vs_age.py

Loops through a healthy control derivatives directory, finds all
'surface_area.mat' files, extracts the 'network_surfacearea' variable
(1x18 double), merges with subject ages from a CSV file, and plots
surface area vs. age (in months) for selected networks  one stacked
subplot per network, sharing a common x-axis.

CSV requirements:
    Must contain columns "subject" and "age_months".
    "subject" values must match the subject folder names found under
    --hc_dir (i.e. the parent directory name of each surface_area.mat file).

Usage:
    python plot_surfacearea_vs_age.py --hc_dir /path/to/controls --csv ages.csv \
        --networks Visual Limbic "Default Mode"

    python plot_surfacearea_vs_age.py --hc_dir /path/to/controls --csv ages.csv \
        --networks Visual --output figure.png
"""

import os
import argparse
import numpy as np
import pandas as pd
import scipy.io as sio
import matplotlib.pyplot as plt

#    Network labels (edit to match your parcellation)                         
NETWORK_LABELS = [
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


def load_surface_areas(data_dir: str):
    """
    Walk *data_dir* recursively, load every 'surface_area.mat' found,
    and stack network_surfacearea rows into a (n_subjects x 18) array.
    Returns (data_array, subject_ids) where subject_ids are the parent
    folder names.
    """
    rows, subjects = [], []

    for root, _, files in os.walk(data_dir):
        for fname in sorted(files):
            if "surface_area.mat" in fname:
                fpath = os.path.join(root, fname)
                try:
                    mat = sio.loadmat(fpath)
                except Exception as exc:
                    print(f"  [warn] Could not load {fpath}: {exc}")
                    continue

                if "network_surfarea" not in mat:
                    print(f"  [warn] 'network_surfarea' missing in {fpath}")
                    continue

                vals = np.asarray(mat["network_surfarea"]).ravel()

                if vals.size != 18:
                    print(f"  [warn] Expected 18 values, got {vals.size} in {fpath}")
                    continue

                rows.append(vals)
                subjects.append(os.path.basename(root))

    if not rows:
        raise FileNotFoundError(
            f"No valid 'surface_area.mat' files found under: {data_dir}"
        )

    data = np.vstack(rows)  # shape: (n_subjects, 18)
    print(f"  Loaded {data.shape[0]} subjects from: {data_dir}")
    return data, subjects


def merge_with_ages(data: np.ndarray, subjects: list[str], csv_path: str):
    """
    Merge surface-area data with ages from CSV (columns: subject, age_months).
    Returns (data_matched, ages_matched, subjects_matched) restricted to
    subjects present in both the data and the CSV.
    """
    df = pd.read_csv(csv_path)

    required_cols = {"subject", "age_months"}
    if not required_cols.issubset(df.columns):
        raise ValueError(
            f"CSV must contain columns {required_cols}, found {list(df.columns)}"
        )

    # Build a lookup: subject -> age_months (as strings to avoid dtype mismatches)
    df["subject"] = df["subject"].astype(str)
    age_lookup = dict(zip(df["subject"], df["age_months"]))

    matched_data, matched_ages, matched_subjects = [], [], []
    missing = []

    for i, subj in enumerate(subjects):
        if subj in age_lookup:
            matched_data.append(data[i])
            matched_ages.append(age_lookup[subj])
            matched_subjects.append(subj)
        else:
            missing.append(subj)

    if missing:
        print(f"  [warn] {len(missing)} subject(s) had no age match in CSV: {missing}")

    if not matched_data:
        raise ValueError("No subjects matched between surface-area data and CSV ages.")

    matched_data = np.vstack(matched_data)
    matched_ages = np.asarray(matched_ages, dtype=float)
    print(f"  Matched {matched_data.shape[0]} subjects to ages.")

    return matched_data, matched_ages, matched_subjects


def plot_surfacearea_vs_age(
    data: np.ndarray,
    ages: np.ndarray,
    labels: list[str],
    output: str | None,
):
    """
    Stacked subplots, one per network, all sharing the same x-axis (age_months).
    """
    n_networks = data.shape[1]

    fig, axes = plt.subplots(
        n_networks, 1,
        figsize=(9, 2.6 * n_networks),
        sharex=True,
    )
    fig.patch.set_facecolor("#F8F8F8")

    # If only one network selected, axes is not a list  normalize to a list
    if n_networks == 1:
        axes = [axes]

    sort_idx = np.argsort(ages)
    ages_sorted = ages[sort_idx]

    for i, ax in enumerate(axes):
        y = data[:, i][sort_idx]

        ax.set_facecolor("#F8F8F8")
        ax.scatter(
            ages_sorted, y,
            s=35,
            color="#3A7ABF",
            alpha=0.75,
            edgecolors="white",
            linewidths=0.4,
            zorder=3,
        )

        # Simple linear trend line to show developmental trajectory
        if len(ages_sorted) >= 2:
            coeffs = np.polyfit(ages_sorted, y, deg=1)
            trend = np.polyval(coeffs, ages_sorted)
            ax.plot(ages_sorted, trend, color="#E05C2A", linewidth=2, zorder=2)

        ax.set_ylabel(labels[i], fontsize=10, rotation=0, ha="right", va="center")
        ax.yaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.6, color="#CCCCCC")
        ax.set_axisbelow(True)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

    axes[-1].set_xlabel("Age (months)", fontsize=11)
    fig.suptitle(
        f"Network surface area vs. age  (n={data.shape[0]} subjects)",
        fontsize=13,
        fontweight="bold",
        y=0.995,
    )

    plt.tight_layout(rect=[0, 0, 1, 0.98])

    if output:
        fig.savefig(output, dpi=150, bbox_inches="tight")
        print(f"Figure saved to: {output}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot network surface area vs. age for healthy controls."
    )
    parser.add_argument(
        "--hc_dir",
        required=True,
        help="Root directory for healthy control surface_area.mat files.",
    )
    parser.add_argument(
        "--csv",
        required=True,
        help="Path to CSV with columns 'subject' and 'age_months'.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the figure (e.g. figure.png). "
             "If omitted, the plot is displayed interactively.",
    )
    parser.add_argument(
        "--labels",
        nargs=18,
        default=None,
        metavar="LABEL",
        help="Custom list of exactly 18 network labels (space-separated).",
    )
    parser.add_argument(
        "--networks",
        nargs="+",
        default=None,
        metavar="NETWORK",
        help=(
            "Names of networks to plot (space-separated, case-insensitive). "
            "If omitted, all 18 networks are plotted (one subplot each). "
            "Example: --networks Visual Limbic \"Default Mode\""
        ),
    )
    args = parser.parse_args()

    labels = args.labels if args.labels else NETWORK_LABELS

    #    Resolve selected network indices                                      
    if args.networks:
        labels_lower = [l.lower() for l in labels]
        indices = []
        for name in args.networks:
            try:
                idx = labels_lower.index(name.lower())
                indices.append(idx)
            except ValueError:
                print(f"  [warn] Network '{name}' not found in labels  skipping.")

        if not indices:
            raise ValueError(
                f"None of the requested networks matched any label. Available: {labels}"
            )

        selected_labels = [labels[i] for i in indices]
        print(f"Plotting {len(indices)} selected networks: {selected_labels}")
    else:
        indices = list(range(len(labels)))
        selected_labels = labels

    print("Loading healthy controls...")
    hc_data, hc_subjects = load_surface_areas(args.hc_dir)

    print("Merging with ages from CSV...")
    hc_data, hc_ages, hc_subjects = merge_with_ages(hc_data, hc_subjects, args.csv)

    # Subset to selected networks
    hc_data = hc_data[:, indices]

    plot_surfacearea_vs_age(hc_data, hc_ages, selected_labels, args.output)


if __name__ == "__main__":
    main()
