"""
Initialize the Flask application and run the server.

Last updated: K. Wheelan, July 2025
"""

from app import app
import os
import warnings
import sys

# make sure gunicorn prints debug statements
print("debug", file=sys.stderr)

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
# Disable all FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
