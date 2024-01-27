@echo off

:: A file to download dependencies and run the python script on a Windows OS

set ROOT=C:\Users\d21285s\Desktop\Katrina\process-xbrl

:: Specify the python version, the virtual environment directory and your python script's file
set PYTHON_VERSION=python
set VENV_DIR=.\xbrl_venv
set PY_SCRIPT=main.py

:: Parameters for the python script
set INPUT_FILE=input_files\acfrs\Clayton_acfr_simple.xlsx
set OUTPUT_FILE=output\Clayton.html
set CONTEXTS_FILE=input_files\contexts.xlsx
set FORMAT=gray

:: Create the virtual environment
%PYTHON_VERSION% -m venv %VENV_DIR%

:: Activate the virtual environment
call %VENV_DIR%\Scripts\Activate

:: Install dependencies
pip install -r reqs.txt

:: Run your python script
python %PY_SCRIPT% --i %INPUT_FILE% --o %OUTPUT_FILE% --f %FORMAT% --c %CONTEXTS_FILE%


set SCRIPT="dependencies\arelle\arelleCmdLine.py"
set PLUGINS="%ROOT%\dependencies\ixbrl-viewer\iXBRLViewerPlugin"
set VIEWER_URL="https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
set FILE_PATH="output\Clayton.html"

:: If you have viewer_filepath variable, define here
set VIEWER_FILEPATH=output\ixbrl-viewer_windows.html

python %SCRIPT% --plugins=%PLUGINS% -f %FILE_PATH% --save-viewer %VIEWER_FILEPATH% --viewer-url %VIEWER_URL%

start %ROOT%\%VIEWER_FILEPATH%