from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
import speech_recognition as sr
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

# Configure upload folder for temporary audio files
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class UppercaseText(Resource):
    def get(self):
        """
        Convert text to uppercase.
        ---
        tags:
        - Text Processing
        parameters:
            - name: text
              in: query
              type: string
              required: true
              description: The text to be converted to uppercase
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            text:
                                type: string
                                description: The text in uppercase
        """
        text = request.args.get('text')
        return jsonify({"text": text.upper()})

class VoiceToText(Resource):
    def post(self):
        """
        Convert a voice file to text.
        ---
        tags:
        - Speech Processing
        consumes:
          - multipart/form-data
        parameters:
          - name: file
            in: formData
            type: file
            required: true
            description: The voice file to convert to text
        responses:
            200:
                description: A successful voice-to-text conversion
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            text:
                                type: string
                                description: The transcribed text from the voice file
        """
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        recognizer = sr.Recognizer()
        text = ""
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
            return jsonify({"text": text})
        except sr.UnknownValueError:
            return jsonify({"error": "Audio not understood"}), 400
        except sr.RequestError:
            return jsonify({"error": "Speech recognition service unavailable"}), 500
        finally:
            time.sleep(0.1)  # Slight delay if needed
            os.remove(file_path)  # Ensure file is removed

api.add_resource(UppercaseText, "/uppercase")
api.add_resource(VoiceToText, "/voicetotext")

if __name__ == "__main__":
    app.run(debug=True)
