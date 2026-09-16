"""
plot_network_surfacearea.py

Loops through two directories (healthy controls and clinical population),
finds all 'surface_area.mat' files, extracts the 'network_surfacearea'
variable (1x18 double), and plots:
  - Box & whisker = healthy control distribution
  - Colored dots  = each clinical subject (one unique color per subject)

Usage:
    python plot_network_surfacearea.py --hc_dir /path/to/controls --clin_dir /path/to/clinical
    python plot_network_surfacearea.py --hc_dir /path/to/controls --clin_dir /path/to/clinical --output figure.png
"""

import os
import argparse
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

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


def load_surface_areas(data_dir: str, subject_list_path=None) -> tuple[np.ndarray, list[str]]:
    """
    Walk *data_dir* recursively, load every 'surface_area.mat' found,
    and stack network_surfacearea rows into a (n_subjects x 18) array.
    Returns (data_array, subject_ids).
    """
    rows, subjects = [], []

    all_subs = True

    if subject_list_path:
        all_subs = False
        with open(subject_list_path, 'r') as file:
            subject_list = file.read().splitlines()

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
                
                if all_subs:
                    rows.append(vals)
                    subjects.append(os.path.basename(root))
                else:
                    sub_ses = '_'.join(fname.split('_')[0:2])
                    if sub_ses in subject_list:
                        rows.append(vals)
                        subjects.append(os.path.basename(root))

    if not rows:
        raise FileNotFoundError(
            f"No valid 'surface_area.mat' files found under: {data_dir}"
        )

    data = np.vstack(rows)   # shape: (n_subjects, 18)
    print(f"  Loaded {data.shape[0]} subjects from: {data_dir}")
    return data, subjects


def plot_surface_areas(
    hc_data: np.ndarray,
    hc_subjects: list[str],
    clin_data: np.ndarray,
    clin_subjects: list[str],
    labels: list[str],
    output: str | None,
):
    """
    Box & whisker from healthy controls; colored dots per clinical subject.
    """
    n_hc, n_networks = hc_data.shape
    n_clin           = clin_data.shape[0]
    x_positions      = np.arange(1, n_networks + 1)

    # ── Assign one distinct color per clinical subject ───────────────────────
    if n_clin <= 10:
        cmap = plt.get_cmap("tab10")
    elif n_clin <= 20:
        cmap = plt.get_cmap("tab20")
    else:
        cmap = plt.get_cmap("turbo")

    clin_colors = [cmap(i / max(n_clin - 1, 1)) for i in range(n_clin)]

    # ── Figure ───────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(16, 6))
    fig.patch.set_facecolor("#F8F8F8")
    ax.set_facecolor("#F8F8F8")

    # ── Box plots (healthy controls) ─────────────────────────────────────────
    ax.boxplot(
        [hc_data[:, i] for i in range(n_networks)],
        positions=x_positions,
        widths=0.5,
        patch_artist=True,
        notch=False,
        showfliers=False,
        medianprops=dict(color="#E05C2A", linewidth=2),
        whiskerprops=dict(color="#555555", linewidth=1.2),
        capprops=dict(color="#555555", linewidth=1.2),
        boxprops=dict(facecolor="#D0E4F5", edgecolor="#3A7ABF", linewidth=1.1),
    )

    # ── Clinical subject dots (one color per subject, consistent across networks)
    rng = np.random.default_rng(42)
    for subj_idx in range(n_clin):
        # Same jitter seed offset per subject so dots visually "track" across networks
        jitter = rng.uniform(-0.22, 0.22, size=n_networks)
        ax.scatter(
            x_positions + jitter,
            clin_data[subj_idx, :],
            s=40,
            color=clin_colors[subj_idx],
            alpha=0.85,
            zorder=4,
            linewidths=0.4,
            edgecolors="white",
            label=clin_subjects[subj_idx],
        )

    # ── Formatting ───────────────────────────────────────────────────────────
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=9)
    ax.set_ylabel("Surface area (mm²)", fontsize=11)
    ax.set_title(
        f"Network surface area  |  HC n={n_hc}  ·  Clinical n={n_clin}",
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
    box_patch = mpatches.Patch(facecolor="#D0E4F5", edgecolor="#3A7ABF", label=f"HC distribution (n={n_hc})")
    med_line  = Line2D([0], [0], color="#E05C2A", linewidth=2, label="HC median")

    clin_handles = [
        Line2D(
            [0], [0],
            marker="o", color="w",
            markerfacecolor=clin_colors[i],
            markeredgecolor="white",
            markersize=7,
            label=clin_subjects[i],
        )
        for i in range(n_clin)
    ]

    all_handles = [box_patch, med_line] + clin_handles

    # For many clinical subjects, place legend outside the axes to avoid overlap
    if n_clin <= 12:
        ax.legend(
            handles=all_handles,
            fontsize=8,
            framealpha=0.7,
            title="Legend",
            title_fontsize=9,
        )
    else:
        ax.legend(
            handles=all_handles,
            fontsize=7,
            framealpha=0.7,
            title="Legend",
            title_fontsize=8,
            bbox_to_anchor=(1.01, 1),
            loc="upper left",
            borderaxespad=0,
        )

    plt.tight_layout()

    if output:
        fig.savefig(output, dpi=150, bbox_inches="tight")
        print(f"Figure saved to: {output}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot network surface areas: HC boxes, clinical colored dots."
    )
    parser.add_argument(
        "--hc_dir",
        required=True,
        help="Root directory for healthy control surface_area.mat files.",
    )
    parser.add_argument(
        "--clin_dir",
        required=True,
        help="Root directory for clinical population surface_area.mat files.",
    )
    parser.add_argument(
        "--hc_subs",
        default=None,
        help="List of healthy control subjects to plot.",
    )
    parser.add_argument(
        "--clin_sub",
        default=None,
        help="Subject ID of the clinical subject to look at.",
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
        help="Names of networks to plot (space-separated, case-insensitive). "
            "Must match entries in NETWORK_LABELS or your custom --labels list. "
            "If omitted, all 18 networks are plotted. "
            "Example: --networks Visual Limbic Frontoparietal \"Default Mode\""
    )
    args = parser.parse_args()

    labels = args.labels if args.labels else NETWORK_LABELS
    
    #    Filter to selected networks                                           
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
                "None of the requested networks matched any label. "
                f"Available: {labels}"
            )

        labels    = [labels[i] for i in indices]
        print(f"Plotting {len(indices)} selected networks: {labels}")
    else:
        indices = list(range(len(labels)))

    print("Loading healthy controls...")
    hc_data, hc_subjects = load_surface_areas(args.hc_dir, args.hc_subs)

    print("Loading clinical population...")
    clin_data, clin_subjects = load_surface_areas(args.clin_dir, args.clin_sub)
    
    # Subset columns to selected networks
    hc_data   = hc_data[:, indices]
    clin_data = clin_data[:, indices]

    plot_surface_areas(hc_data, hc_subjects, clin_data, clin_subjects, labels, args.output)


if __name__ == "__main__":
    main()
