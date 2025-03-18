#!/bin/bash
RAW_DATA_DIR="raw_data"
PY_SCRIPT="py_script.py"
REQUIREMENTS="requirements.txt"

# Check if requirements.txt exists
if [ ! -f "$REQUIREMENTS" ]; then
    echo "Error: $REQUIREMENTS file not found."
    exit 1
fi

# Install required Python libraries
pip3 install -r "$REQUIREMENTS"

# Verify raw data directory exists
if [ ! -d "$RAW_DATA_DIR" ]; then
    echo "Error: Directory $RAW_DATA_DIR does not exist."
    exit 1
fi

# Process each CSV file
csv_found=false
for file in "$RAW_DATA_DIR"/*.csv; do
    if [ ! -f "$file" ]; then
        continue
    fi

    csv_found=true

    filename=$(basename -- "$file")
    filename_no_ext="${filename%.csv}"

    output_file_csv="${filename_no_ext}_output.csv"
    output_file_boxplot="${filename_no_ext}_boxplot.png"

    echo "Processing $file -> $output_file_csv"
    python3 "$PY_SCRIPT" "$file" "$output_file_csv" "$output_file_boxplot"
done

if [ "$csv_found" = false ]; then
    echo "No CSV files found in $RAW_DATA_DIR."
    exit 1
fi

echo "All files processed."
