import json
import os
import ast
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Paths to your data files
USER_PROGRESS_FILE = "user_progress.json" 

def safe_json_load(file_path):
    """Safely loads a JSON file, returning an empty list if it's empty or invalid."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r") as f:
            if os.fstat(f.fileno()).st_size == 0:
                return []
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []



@app.route("/get_user_progress", methods=["GET"])
def get_user_progress():
    """Returns the content of the user_progress.json file."""
    return jsonify(safe_json_load(USER_PROGRESS_FILE))


if __name__ == "__main__":
    app.run(debug=True)