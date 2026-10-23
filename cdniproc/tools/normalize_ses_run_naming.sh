#!/bin/bash

# Root directory to start walking (default is current dir)
root_dir="${1:-.}"

echo $root_dir

# Rename folders like ses-1  ses-01, run-2  run-02
normalize_folder_names() {
    find "$1" -depth -type d | while read -r dir; do
        base="$(basename "$dir")"
        parent="$(dirname "$dir")"

        if [[ "$base" =~ ^(ses|run)-([0-9])$ ]]; then
            prefix="${BASH_REMATCH[1]}"
            num="${BASH_REMATCH[2]}"
            new_base="${prefix}-0${num}"
            new_path="${parent}/${new_base}"

            if [ ! -e "$new_path" ]; then
                echo "Renaming folder: $dir  $new_path"
                mv "$dir" "$new_path"
            else
                echo "Skipping folder rename (target exists): $new_path"
            fi
        fi
    done
}

# Rename files like ses-1_something.nii  ses-01_something.nii
normalize_file_names() {
    find "$1" -depth -type f | while read -r file; do
        base="$(basename "$file")"
        dir="$(dirname "$file")"
        new_base="$base"

        # Replace ses-1 with ses-01
        if [[ "$new_base" =~ ses-([0-9])\b ]]; then
            new_base="${new_base/ses-${BASH_REMATCH[1]}/ses-0${BASH_REMATCH[1]}}"
        fi

        # Replace run-1 with run-01
        if [[ "$new_base" =~ run-([0-9])\b ]]; then
            new_base="${new_base/run-${BASH_REMATCH[1]}/run-0${BASH_REMATCH[1]}}"
        fi

        if [[ "$new_base" != "$base" ]]; then
            new_path="${dir}/${new_base}"
            if [ ! -e "$new_path" ]; then
                echo "Renaming file: $file  $new_path"
                mv "$file" "$new_path"
            else
                echo "Skipping file rename (target exists): $new_path"
            fi
        fi
    done
}

# Run both functions in sequence
echo normalize_folder_names $root_dir
normalize_folder_names $root_dir
echo normalize_file_names "$root_dir"
normalize_file_names "$root_dir"
