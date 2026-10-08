from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

import os
import io


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CREATE FLASK APP
# ==========================================

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)


# ==========================================
# AZURE STORAGE SETTINGS
# ==========================================

AZURE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

AZURE_CONTAINER_NAME = os.getenv(
    "AZURE_CONTAINER_NAME",
    "cloud-backup"
)


# ==========================================
# CHECK AZURE CONNECTION STRING
# ==========================================

if not AZURE_CONNECTION_STRING:
    raise ValueError(
        "AZURE_STORAGE_CONNECTION_STRING is not set"
    )


# ==========================================
# CONNECT TO AZURE BLOB STORAGE
# ==========================================

blob_service_client = BlobServiceClient.from_connection_string(
    AZURE_CONNECTION_STRING
)

container_client = blob_service_client.get_container_client(
    AZURE_CONTAINER_NAME
)


# ==========================================
# HOME / TEST
# ==========================================

@app.route("/")
def home():

    return jsonify({
        "message": "Cloud Backup Backend is running!"
    })


# ==========================================
# UPLOAD FILE
# ==========================================

@app.route("/api/upload", methods=["POST"])
def upload_file():

    try:

        if "file" not in request.files:

            return jsonify({
                "success": False,
                "message": "No file selected"
            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "message": "Invalid filename"
            }), 400

        filename = file.filename

        blob_client = container_client.get_blob_client(
            filename
        )

        blob_client.upload_blob(
            file,
            overwrite=True
        )

        return jsonify({
            "success": True,
            "message": "File uploaded successfully",
            "filename": filename
        })

    except Exception as e:

        print("UPLOAD ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# LIST FILES
# ==========================================

@app.route("/api/files", methods=["GET"])
def get_files():

    try:

        files = []

        blobs = container_client.list_blobs()

        for blob in blobs:

            files.append({
                "name": blob.name,
                "size": blob.size,
                "url":
                    f"https://cloudBackupphotoswebsite.azurewebsites.net/api/download/{blob.name}"
            })

        return jsonify({
            "success": True,
            "files": files
        })

    except Exception as e:

        print("LIST ERROR:", e)

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================================
# DOWNLOAD / VIEW FILE
# ==========================================

@app.route(
    "/api/download/<path:filename>",
    methods=["GET"]
)
def download_file(filename):

    try:

        blob_client = container_client.get_blob_client(
            filename
        )

        download_stream = blob_client.download_blob()

        file_data = download_stream.readall()

        return send_file(
            io.BytesIO(file_data),
            download_name=filename,
            as_attachment=False
        )

    except Exception as e:

        print("DOWNLOAD ERROR:", e)

        return jsonify({
            "success": False,
            "message": "File not found"
        }), 404


# ==========================================
# DELETE FILE
# ==========================================

@app.route(
    "/api/delete/<path:filename>",
    methods=["DELETE"]
)
def delete_file(filename):

    try:

        blob_client = container_client.get_blob_client(
            filename
        )

        blob_client.delete_blob()

        return jsonify({
            "success": True,
            "message": "File deleted successfully"
        })

    except Exception as e:

        print("DELETE ERROR:", e)

        return jsonify({
            "success": False,
            "message": "File could not be deleted"
        }), 404


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
