from flask import Flask, request, jsonify, send_from_directory
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

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    cleaned_file_path = os.path.join(app.config["UPLOAD_FOLDER"], f"cleaned_{filename}")
    command = ["exiftool", "-all=", "-overwrite_original", "-out", cleaned_file_path, file_path]

    try:
        subprocess.run(command, check=True)
        return jsonify({"message": "File metadata removed", "file_path": f"/uploads/cleaned_{filename}"}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Failed to process file", "details": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)  

@app.route('/uploads/<filename>', methods=['GET'])
def get_cleaned_file(filename):
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host="0.0.0.0", port=port, debug=True)
