#!/bin/bash

# Root directory to operate on (default: current dir)
root_dir="${1:-.}"

normalize_file_names() {
    find "$root_dir" -type f | while IFS= read -r file; do
        dir="$(dirname "$file")"
        base="$(basename "$file")"

        # Apply sed substitutions directly
        new_base="$(echo "$base" | sed -E 's/ses-([0-9])(?![0-9])/ses-0\1/g; s/run-([0-9])(?![0-9])/run-0\1/g')"
        echo $base
        echo $new_base

        if [[ "$new_base" != "$base" ]]; then
            new_path="${dir}/${new_base}"
            if [ ! -e "$new_path" ]; then
                echo "Renaming file: \"$file\"  \"$new_path\""
                mv "$file" "$new_path"
            else
                echo "Skipping (target exists): \"$new_path\""
            fi
        fi
    done
}

normalize_file_names
