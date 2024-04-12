"""App entry point."""
from games import create_app
import os

app = create_app()

if __name__ == "__main__":
    app.config['SECRET_KEY'] = os.urandom(32)
    app.run(host='localhost', port=5000, threaded=False)
