"""
Initialize the Flask application and run the server.

K. Wheelan 2024
"""

from app import app
import os

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
