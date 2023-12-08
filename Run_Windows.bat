@echo off

:: A file to download dependencies and run the python script on a Windows OS

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