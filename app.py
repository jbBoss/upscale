from __future__ import annotations

import mimetypes
import tempfile
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request, send_file
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename

from processor import upscale_image

def log_action(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}
MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index() -> str:
    log_action("Homepage accessed")
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_image():
    log_action("Image processing request received")

    if "image" not in request.files:
        log_action("Error: No file uploaded")
        abort(400, description="No file uploaded")

    file_storage = request.files["image"]

    if file_storage.filename == "":
        log_action("Error: Empty filename")
        abort(400, description="Empty filename")

    if not allowed_file(file_storage.filename):
        log_action(f"Error: Unsupported file type for file {file_storage.filename}")
        abort(415, description="Unsupported file type")

    filename = secure_filename(file_storage.filename)
    log_action(f"Processing file: {filename}")

    # Create a temporary directory that will persist until the response is sent
    tmp_dir = tempfile.mkdtemp()
    try:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / filename
        file_storage.save(input_path)
        log_action(f"File saved to temporary directory: {input_path}")

        output_name = f"upscaled_{input_path.stem}.png"
        output_path = tmp_path / output_name
        log_action("Starting image upscaling process")

        upscale_image(input_path, output_path)
        log_action("Image upscaling completed")

        mimetype = mimetypes.types_map.get(".png", "image/png")
        log_action("Sending processed image back to client")

        def cleanup_after_request(response):
            try:
                # Clean up the temporary files after the response is sent
                if input_path.exists():
                    input_path.unlink()
                if output_path.exists():
                    output_path.unlink()
                tmp_path.rmdir()
                log_action("Cleaned up temporary files")
            except Exception as e:
                log_action(f"Error cleaning up temporary files: {str(e)}")
            return response

        response = send_file(output_path, mimetype=mimetype)
        response.call_on_close(cleanup_after_request)
        return response

    except Exception as e:
        # Clean up in case of errors
        try:
            if 'input_path' in locals() and input_path.exists():
                input_path.unlink()
            if 'output_path' in locals() and output_path.exists():
                output_path.unlink()
            tmp_path.rmdir()
        except:
            pass
        raise


@app.errorhandler(Exception)
def handle_exception(exc: Exception):
    if isinstance(exc, HTTPException):
        log_action(f"HTTP Error {exc.code}: {exc.description}")
        response = jsonify({"error": exc.description})
        response.status_code = exc.code
        return response

    log_action(f"Unexpected server error: {str(exc)}")
    response = jsonify({"error": "Unexpected server error"})
    response.status_code = 500
    return response


if __name__ == "__main__":
    app.run(debug=True)
