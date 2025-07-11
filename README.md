Copyright © <2024> The Regents of the University of Michigan

Last updated: May 2025

## Purpose

An open-source tool to convert ACFR files in Excel and Word into inline XBRL

## Demo

View the app on Heroku here: [https://xbrl-converter-22f50351e04c.herokuapp.com/](https://xbrl-converter-22f50351e04c.herokuapp.com/)
or embedded on the CLOSUP site here: [https://closup.umich.edu/acfr-tool](https://closup.umich.edu/acfr-tool)

## To Run Locally

1. Package requirements are listed in requirements.txt; create a new virtual environment and download these using pip:
```
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```
2. Initialize submodules:
```
git submodule init
git submodule update
```
3. Run the main.py script:
```
python3 main.py
```
4. This will launch a Flask server -- open a web browser and navigate to the address given in the terminal output (http://127.0.0.1:8080/)
5. You can test the functionality by uploading the sample file where prompted on the app: `static/input_files/samples/Clayton_sample.xlsx`

## Running into issues?
There may be an issue with FLASK_SECRET_KEY. If you are running into issues, generate a .env file and set the FLASK_SECRET_KEY to a 32 character string that can be generated via `python -c "import secrets; print(secrets.token_hex(16))"` in terminal.

## File structure

```
/process-xbrl
    /app
        __init__.py  # Initialize the Flask application and its components.
        routes.py    # Route definitions for the Flask application 
        /models 
            __init__.py 
            ...  # Classes to represent different data structures (Cell, Table, etc)
        /templates
            /site
                ...  # HTML templates for rendering views in the Flask app
            /xbrl
                ...  # jinja2 HTML templates for formatting the converted inline XBRL
        /static
            /js
                ... # javascript functions
            /css
                ... # css styling for the web app
            /input_files
                ACFR_template.xlsx # The downloadable excel template for a complete ACFR
                /samples
                    ... # sample excel ACFRs to test the site
                    /word_documents 
                        ... # sample word docs to test the site
            /output
                output.html # The converted iXBRL document created by the app
                ixbrl-viewer.html # generated webpage to interactively view the converted docs
        /utils
            __init__.py
            constants.py    # Constants used throughout the app.
            helper_functions.py  # Common utility functions reused in the app.
            xbrl_processing.py  # Functions to do the excel to iXBRL conversion
    /dependencies  # Git submodules
        /Arelle
            ... # An open source repo to validate the taxonomy (https://github.com/Arelle/Arelle)
        /ixbrl-viewer
            ... # a repo that helps create the interactive viewer (https://github.com/Arelle/ixbrl-viewer)
        ...
    main.py  # Main entry point for running the Flask app
    requirements.txt  # Lists the Python dependencies for `pip install`
    .gitmodules # tells the app about the submodules
    .github/changelog.yml # tells the app to update the changelog when a PR is merged
    .gitignore # tells the app to ignore certain files
    app.json # tells Heroku to initialize the submodules when deloying the app
    Procfile # required for Heroku deployment
    CHANGELOG.md # changelog for the app automatically generated by the release-changelog-builder-action
```

## Branches

- `main` is the production branch which is deployed on the CLOSUP website.
- `dev` is the development branch which is used for development.

## Resources

See the Drive folder [here](https://drive.google.com/drive/folders/1oyI5-ivM86TF-zFTMOrO20etBB2uIb5B)
