from flask import Flask, request, send_file
import os
from werkzeug.utils import secure_filename
import imghdr
import cv2
from pixelate_faces import pixelate_faces, pixelate_faces_video_dnn

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "processed"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return {"error": "No file provided"}, 400

    file = request.files["file"]
    anonymize_faces = request.form.get("anonymize_faces", "false").lower() == "true"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, f"clean_{filename}")

        file.save(input_path)

        file_type = imghdr.what(input_path)

        if file_type in ['jpeg', 'png', 'gif', 'bmp']:
            if anonymize_faces:
                pixelate_faces(input_path, output_path)
            else:
                os.rename(input_path, output_path)
        else:
            if anonymize_faces:
                pixelate_faces_video_dnn(input_path, output_path)
            else:
                os.rename(input_path, output_path)

        return send_file(output_path, as_attachment=True)

    return {"error": "Invalid file type or file processing failed"}, 400

if __name__ == "__main__":
    app.run(debug=True)
