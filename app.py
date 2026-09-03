import os

from Backend.app import app


if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', '0') == '1',
        port=int(os.getenv('PORT', '5000')),
        use_reloader=False,
    )
