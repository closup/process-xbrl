
Last updated: December 14, 2023

Katrina Wheelan

## Purpose

An open-source tool to convert Excel into XBRL

## To Run

### 1. Download the repository from GitHub

 - Visit the repository's GitHub page at [https://github.com/closup/process-xbrl](https://github.com/closup/process-xbrl)
 - Click the green "Code" button, and then select "Download ZIP" to download a ZIP archive of the repository to your local machine.
 - Extract the downloaded ZIP archive to a location of your choice on your computer.

 ### 2. Download dependencies

  - [Python](https://www.python.org/downloads/)
  - [git](https://git-scm.com/downloads)

 ### 3. Run the script

If running Windows:
 - open `Run_Windows.cmd`
 - adjust any of the parameters set in this file
 - run the script by either double clicking the `Run_Windows.cmd` file in your file explorer or by typing `Run_Windows.cmd` into your Windows command prompt and hitting enter
 - If using Anaconda, run in Anaconda Prompt, not Anaconda Powershell

 If running OSX or Linux:
 - open `Run_OSX_Linux.sh`
 - adjust any of the parameters set in this file
 - run the script by typing and `Run_OSX_Linux.sh` into your terminal and hitting enter

### 4. Open the output file

 - The script should automatically open your file within an ixbrl-viewer browser window.
 - The resulting output HTML file will also be generated in the "output" directory. You can locate the output file at the following path: `output/Clayton.html`
 - You can open this HTML file in a web browser or Arelle to view the results.
