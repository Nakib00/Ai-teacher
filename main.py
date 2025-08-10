import json
import os
import ast
from flask import Flask, jsonify, request

app = Flask(__name__)

# --- File Paths ---
USER_PROGRESS_FILE = "user_progress.json"
EDUCATIONAL_DATA_FILE = "educational_data.py"

# --- Helper Functions ---

def safe_json_load(file_path):
    """
    Safely loads a JSON file.
    Returns the data if successful, or None if the file doesn't exist or is invalid.
    """
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if os.fstat(f.fileno()).st_size == 0:
                return []
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def get_educational_data_dict():
    """
    Reads and safely evaluates the educational_data.py file content.
    Returns the dictionary or None on error.
    """
    try:
        with open(EDUCATIONAL_DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            # Find the start of the dictionary and safely evaluate it
            dict_start = content.find('{')
            if dict_start == -1:
                return None
            return ast.literal_eval(content[dict_start:])
    except (IOError, FileNotFoundError, SyntaxError):
        return None

def save_educational_data_dict(data):
    """
    Saves the dictionary back to the educational_data.py file.
    Returns True on success, False on error.
    """
    try:
        # Format the data as a pretty-printed string
        new_content = "educational_data = " + json.dumps(data, indent=4)
        with open(EDUCATIONAL_DATA_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except IOError:
        return False

# --- API Endpoints ---

@app.route("/get_user_progress", methods=["GET"])
def get_user_progress():
    """Returns the content of the user_progress.json file in a structured format."""
    progress_data = safe_json_load(USER_PROGRESS_FILE)

    if progress_data is not None:
        response = {
            'success': True,
            'status': 200,
            'message': 'User progress retrieved successfully.',
            'data': progress_data,
            'errors': None
        }
        return jsonify(response), 200
    else:
        response = {
            'success': False,
            'status': 404,
            'message': 'Could not find or read user progress file.',
            'data': None,
            'errors': {'file': 'user_progress.json not found or is invalid.'}
        }
        return jsonify(response), 404

@app.route("/get_educational_data", methods=["GET"])
def get_educational_data():
    """Returns the content of the educational_data.py file."""
    edu_data = get_educational_data_dict()

    if edu_data is not None:
        response = {
            'success': True,
            'status': 200,
            'message': 'Educational data retrieved successfully.',
            'data': edu_data,
            'errors': None
        }
        return jsonify(response), 200
    else:
        response = {
            'success': False,
            'status': 404,
            'message': 'Could not read educational data file.',
            'data': None,
            'errors': {'file': 'educational_data.py not found or is invalid.'}
        }
        return jsonify(response), 404

@app.route("/update_educational_data", methods=["POST"])
def update_educational_data():
    """Updates the educational_data.py file with new data from the request."""
    new_data = request.get_json()

    if not new_data:
        response = {
            'success': False,
            'status': 400,
            'message': 'Bad Request: No data provided.',
            'data': None,
            'errors': {'request': 'Request body must contain valid JSON.'}
        }
        return jsonify(response), 400

    if save_educational_data_dict(new_data):
        response = {
            'success': True,
            'status': 200,
            'message': 'Educational data updated successfully.',
            'data': new_data,
            'errors': None
        }
        return jsonify(response), 200
    else:
        response = {
            'success': False,
            'status': 500,
            'message': 'Internal Server Error: Could not write to file.',
            'data': None,
            'errors': {'file': 'Failed to save educational_data.py.'}
        }
        return jsonify(response), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)