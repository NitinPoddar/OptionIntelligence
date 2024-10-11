import sys
import os

# Add the directory for your Flask app to sys.path
sys.path.insert(0, os.path.dirname('techacin/home/public_html/myflaskapp'))

# Import your Flask application instance
from main import app as application
