# Read Me

## Purpose

An open-source tool to conver Excel into XBRL

## To Run

### 1. Download the repositiry from GitHub

 - Visit the repository's GitHub page at [https://github.com/closup/process-xbrl](https://github.com/closup/process-xbrl)
 - Click the green "Code" button, and then select "Download ZIP" to download a ZIP archive of the repository to your local machine.
 - Extract the downloaded ZIP archive to a location of your choice on your computer.

 ### 2. Create a new conda environment with all the required packages

  - If you don't already have conda, install it from [the Miniconda download page](https://docs.conda.io/projects/miniconda/en/latest/).
  - Open your terminal or command prompt.
  - Navigate to the directory where you extracted the repository using the cd command.
  - Use the following command to create a new conda environment named "xbrl" based on the requirements.txt file:

```conda create --name xbrl --file requirements.txt```

 - Conda will download and install the required packages into the "xbrl" environment.

 ### 3. Run the script

  Once the conda environment is set up, you can run the Python script with the specified arguments. The script is named main.py. Follow these steps:

  - Activate the "xbrl" conda environment by using the following command: `conda activate xbrl`
  - Run the script with the provided command and arguments: `python3 main.py --i input_files/acfrs/Clayton_acfr_simple.xlsx --o output/Clayton.html --f "gray"`

The `--i` flag specifies the input Excel document, the `--o` flag specifies the output file path, and the optional `--f` flag specifies the format options ("gray", "color", or "None").

### 4. Open the output file

 - After running the script, the resulting output HTML file will be generated in the "output" directory. You can locate the output file at the following path: `output/Clayton.html`
 - You can open this HTML file in a web browser or Arelle to view the results.