#!/usr/bin/env python3
"""
Single TSV Acquisition Time Reporter (Variable Input)
------------------------------------------------------
Reads a metadata TSV file specified by a variable or command-line argument,
identifies AcquisitionTime groups with inconsistent labeled scans, calculates
minimum 'fsl_dim4' volume counts, and prints the report directly to the console.
"""

from pathlib import Path
import sys
import pandas as pd


def print_tsv_acq_groups(tsv_filepath: str) -> None:
    """
    Parses a BIDS metadata TSV file, groups files by AcquisitionTime,
    computes minimum fsl_dim4 values, and prints the formatted report to the console.

    Parameters:
    -----------
    tsv_filepath : str
        Path to the input .tsv file.
    """
    path = Path(tsv_filepath)

    # 1. Verify that the input file exists
    if not path.exists():
        print(f"Error: Input file '{tsv_filepath}' does not exist.")
        return

    # 2. Read tab-separated file into a pandas DataFrame
    df = pd.read_csv(path, sep='\t')

    # 3. Verify required columns exist
    required_cols = ['label', 'consistent', 'fsl_dim4', 'AcquisitionTime']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing required column(s) in TSV: {missing_cols}")
        return

    # 4. Standardize column data types
    df['fsl_dim4'] = pd.to_numeric(df['fsl_dim4'], errors='coerce')
    consistent_str = df['consistent'].astype(str).str.strip()

    # 5. Identify labeled rows and inconsistent rows
    has_label = df['label'].notna() & (df['label'].astype(str).str.strip() != '')
    is_inconsistent = consistent_str.isin(['0', '0.0'])

    # 6. Find all AcquisitionTime timestamps where AT LEAST ONE labeled scan has consistent == 0
    flagged_acq_times = df[has_label & is_inconsistent]['AcquisitionTime'].dropna().unique()

    if len(flagged_acq_times) == 0:
        print("No acquisition times found with inconsistent labeled scans (consistent == 0).")
        return

    # 7. Select ALL labeled scans sharing those flagged AcquisitionTime values
    matching_df = df[has_label & df['AcquisitionTime'].isin(flagged_acq_times)].copy()

    # 8. Compute global minimum volume count
    global_min_dim4 = int(matching_df['fsl_dim4'].min())

    # 9. Format report text
    report_lines = []
    report_lines.append("=" * 65)
    report_lines.append("TSV FSL_DIM4 REPORT (ACQUISITION TIME GROUPS)")
    report_lines.append("=" * 65)
    report_lines.append(f"Input File              : {path.name}")
    report_lines.append(f"Flagged AcquisitionTimes: {len(flagged_acq_times)}")
    report_lines.append(f"Total Files Included    : {len(matching_df)}")
    
    report_lines.append("\n" + "-" * 65)
    report_lines.append("GLOBAL MINIMUM VOLUME COUNT")
    report_lines.append("-" * 65)
    report_lines.append(f"Overall Minimum fsl_dim4 across all flagged groups: {global_min_dim4}")

    report_lines.append("\n" + "-" * 65)
    report_lines.append("ACQUISITION TIME GROUP SUMMARY")
    report_lines.append("-" * 65)

    grouped = matching_df.groupby('AcquisitionTime')

    for acq_time, group in grouped:
        min_dim4 = int(group['fsl_dim4'].min())
        series_ids = ", ".join(group['SeriesNumber'].astype(str).unique()) if 'SeriesNumber' in group.columns else 'N/A'
        consistent_statuses = ", ".join(group['consistent'].astype(str).unique())
        labels = ", ".join(group['label'].unique())

        report_lines.append(
            f"AcquisitionTime: {acq_time} | Label(s): {labels:<5} | Series: [{series_ids}] | "
            f"Consistent flags: [{consistent_statuses}] | Min fsl_dim4: {min_dim4}"
        )

    report_lines.append("\n" + "-" * 65)
    report_lines.append("DETAILED ROW BREAKDOWN BY ACQUISITION TIME")
    report_lines.append("-" * 65)

    for acq_time, group in grouped:
        report_lines.append(f"\n[AcquisitionTime: {acq_time}]")
        for _, row in group.iterrows():
            s_num = row.get('SeriesNumber', 'N/A')
            echo = row.get('EchoNumber', 'N/A')
            c_val = row.get('consistent', 'N/A')
            dim4 = int(row['fsl_dim4']) if pd.notna(row['fsl_dim4']) else 'N/A'
            fname = row.get('filename', 'N/A')
            report_lines.append(
                f"  Series {s_num:<2} | Echo {echo} | consistent: {c_val} | fsl_dim4: {dim4} | File: {fname}"
            )

    # 10. Output results directly to standard output
    print("\n".join(report_lines))


if __name__ == "__main__":
    # Define input TSV variable
    input_tsv_file = "1000401_4.tsv"

    # Allow overriding via command-line argument if provided
    if len(sys.argv) > 1:
        input_tsv_file = sys.argv[1]

    # Execute main function
    print_tsv_acq_groups(input_tsv_file)