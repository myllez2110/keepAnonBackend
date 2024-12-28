from flask import Flask, request, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
from flask_cors import CORS  

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    cleaned_file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"cleaned_{filename}")
    command = ["exiftool", "-all=", "-overwrite_original", "-out", cleaned_file_path, file_path]

    try:
        subprocess.run(command, check=True)
        return jsonify({"message": "File metadata removed", "file_path": cleaned_file_path}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to process file", "details": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(debug=True)
