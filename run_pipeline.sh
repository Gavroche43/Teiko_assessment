#!/bin/bash
RAW_DATA_DIR="raw_data"
PY_SCRIPT="py_script.py"

if [ ! -d "$RAW_DATA_DIR" ]; then
    echo "Error: Directory $RAW_DATA_DIR does not exist."
    exit 1
fi

for file in "$RAW_DATA_DIR"/*.csv; do
    if [ ! -f "$file" ]; then
        echo "No CSV files found in $RAW_DATA_DIR."
        exit 1
    fi

    filename=$(basename -- "$file")
    filename_no_ext="${filename%.csv}"

    output_file_csv="${filename_no_ext}_output.csv"
    output_fil_boxplot="${filename_no_ext}_boxplot.png"

    echo "Processing $file -> $output_file_csv"
    python3 "$PY_SCRIPT" "$file" "$output_file_csv" "$output_fil_boxplot"
done

echo "All files processed."
