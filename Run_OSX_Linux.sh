#!/bin/bash

# Specify the python version, the virtual environment directory and your python script's file
PYTHON_VERSION=python3
VENV_DIR=./xbrl_venv
PY_SCRIPT=main.py

# Parameters for the python script
INPUT_FILE="input_files/acfrs/Clayton_acfr_custom.xlsx"
OUTPUT_FILE="output/Clayton.html"
CONTEXTS_FILE="input_files/contexts.xlsx"
FORMAT="gray"

# Create the virtual environment
$PYTHON_VERSION -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install dependencies
pip install -r reqs.txt

# Run your python script
python $PY_SCRIPT --i $INPUT_FILE --o $OUTPUT_FILE --f $FORMAT --c $CONTEXTS_FILE
