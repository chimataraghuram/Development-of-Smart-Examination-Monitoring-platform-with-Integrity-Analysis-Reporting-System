"""Launch the Flask application from the repository root."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from Backend.app import app
except ImportError:
    from backend.app import app

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode, port=int(os.getenv('PORT', '5000')), use_reloader=False)
