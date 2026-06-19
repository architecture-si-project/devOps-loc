from user_app import create_app
from flask_cors import CORS


app = create_app()
CORS(app, origins=["http://localhost:3000"])


if __name__ == "__main__":
    port = "5000"
    debug_value = "True"
    debug = str(debug_value).strip().lower() in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=port, debug=debug)
