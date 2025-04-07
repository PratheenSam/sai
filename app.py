from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('output', exist_ok=True)
os.makedirs('static', exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/text')
def text_steg():
    return render_template('text.html')

@app.route('/image')
def image_steg():
    return render_template('image.html')

@app.route('/audio')
def audio_steg():
    return render_template('audio.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

def register_api_routes():
    from text_stego import text_routes
    from image_stego import image_routes
    from audio_stego import audio_routes
    
    app.register_blueprint(text_routes, url_prefix='/text_api')
    app.register_blueprint(image_routes, url_prefix='/image_api')
    app.register_blueprint(audio_routes, url_prefix='/audio_api')

if __name__ == '__main__':
    register_api_routes()
    app.run(host='0.0.0.0', port=5000, debug=True)