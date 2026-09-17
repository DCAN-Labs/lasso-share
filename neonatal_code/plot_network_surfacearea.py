"""
plot_network_surfacearea.py

Loops through a directory, finds all 'surface_area.mat' files, extracts the
'network_surfacearea' variable (1x18 double), and plots the distribution of
surface areas across subjects for each of the 18 brain networks.

Usage:
    python plot_network_surfacearea.py --data_dir /path/to/your/data
    python plot_network_surfacearea.py --data_dir /path/to/your/data --output figure.png
"""

import os
import argparse
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Network labels (edit to match your parcellation) ────────────────────────
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


def load_surface_areas(data_dir: str) -> tuple[np.ndarray, list[str]]:
    """
    Walk *data_dir* recursively, load every 'surface_area.mat' found,
    and stack network_surfacearea rows into a (n_subjects x 18) array.
    Returns (data_array, subject_ids).
    """
    rows, subjects = [], []

    for root, _, files in os.walk(data_dir):
        for fname in files:
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
                    print(
                        f"  [warn] Expected 18 values, got {vals.size} in {fpath}"
                    )
                    continue

                rows.append(vals)
                # Use the immediate parent folder name as the subject ID
                subjects.append(os.path.basename(root))

    if not rows:
        raise FileNotFoundError(
            f"No valid 'surface_area.mat' files found under: {data_dir}"
        )

    data = np.vstack(rows)          # shape: (n_subjects, 18)
    print(f"Loaded {data.shape[0]} subjects, {data.shape[1]} networks.")
    return data, subjects


def plot_surface_areas(data: np.ndarray, labels: list[str], output: str | None):
    """
    Creates a combined box + strip plot: one column per network,
    x-axis = network name, y-axis = surface area (mm²).
    """
    n_subjects, n_networks = data.shape
    x_positions = np.arange(1, n_networks + 1)

    fig, ax = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor("#F8F8F8")
    ax.set_facecolor("#F8F8F8")

    # ── Box plots ────────────────────────────────────────────────────────────
    bp = ax.boxplot(
        [data[:, i] for i in range(n_networks)],
        positions=x_positions,
        widths=0.45,
        patch_artist=True,
        notch=False,
        showfliers=False,       # outliers shown as individual dots below
        medianprops=dict(color="#E05C2A", linewidth=2),
        whiskerprops=dict(color="#555555", linewidth=1.2),
        capprops=dict(color="#555555", linewidth=1.2),
        boxprops=dict(facecolor="#D0E4F5", edgecolor="#3A7ABF", linewidth=1.1),
    )

    # ── Individual subject dots (jittered) ───────────────────────────────────
    rng = np.random.default_rng(42)
    for i, xpos in enumerate(x_positions):
        jitter = rng.uniform(-0.18, 0.18, size=n_subjects)
        ax.scatter(
            xpos + jitter,
            data[:, i],
            s=18,
            color="#3A7ABF",
            alpha=0.55,
            zorder=3,
            linewidths=0,
        )

    # ── Formatting ───────────────────────────────────────────────────────────
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Surface area (mm²)", fontsize=11)
    ax.set_title(
        f"Network surface area across {n_subjects} subjects",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlim(0.3, n_networks + 0.7)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.7, color="#CCCCCC")
    ax.set_axisbelow(True)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

    # ── Legend ───────────────────────────────────────────────────────────────
    box_patch   = mpatches.Patch(facecolor="#D0E4F5", edgecolor="#3A7ABF", label="IQR (25–75%)")
    dot_patch   = mpatches.Patch(color="#3A7ABF", alpha=0.55, label="Individual subject")
    med_line    = plt.Line2D([0], [0], color="#E05C2A", linewidth=2, label="Median")
    ax.legend(handles=[box_patch, dot_patch, med_line], fontsize=9, framealpha=0.6)

    plt.tight_layout()

    if output:
        fig.savefig(output, dpi=150, bbox_inches="tight")
        print(f"Figure saved to: {output}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="Plot network surface areas across subjects.")
    parser.add_argument(
        "--data_dir",
        required=True,
        help="Root directory to search for surface_area.mat files.",
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
    args = parser.parse_args()

    labels = args.labels if args.labels else NETWORK_LABELS

    data, subjects = load_surface_areas(args.data_dir)
    plot_surface_areas(data, labels, args.output)


if __name__ == "__main__":
    main()
