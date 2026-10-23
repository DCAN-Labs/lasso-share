import json
import os
import sys

# Accept output path from command-line argument, or prompt the user if not provided
if len(sys.argv) > 1:
    output_path = sys.argv[1]
else:
    output_path = input("Enter output path for dataset_description.json: ").strip()
    
filename = os.path.join(output_path,'dataset_description.json')

bids_description = {
    "Acknowledgements": "TODO: whom you want to acknowledge",
    "Authors": [
        "TODO:",
        "First1 Last1",
        "First2 Last2",
        "..."
    ],
    "BIDSVersion": "1.0.1",
    "DatasetDOI": "TODO: eventually a DOI for the dataset",
    "Funding": [
        "TODO",
        "GRANT #1",
        "GRANT #2"
    ],
    "HowToAcknowledge": "TODO: describe how to acknowledge -- either cite a corresponding paper, or just in acknowledgement section",
    "License": "TODO: choose a license, e.g. PDDL (http://opendatacommons.org/licenses/pddl/)",
    "Name": "TODO: name of the dataset",
    "ReferencesAndLinks": [
        "TODO",
        "List of papers or websites"
    ]
}

# Check if the file already exists
if os.path.exists(filename):
    print(f"Dataset_description exists at '{output_path}'. Skipping file creation.")
else:
    # Ensure destination directory exists before saving
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Write to specified file path
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(bids_description, f, indent=4)

    print(f"Saved dataset description to: {output_path}")