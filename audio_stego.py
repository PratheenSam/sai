from flask import Blueprint, request, send_file
from flask_cors import cross_origin
from scipy.io import wavfile
import numpy as np
import os

audio_routes = Blueprint('audio_routes',  __name__)

@audio_routes.route('/hide_audio', methods=['POST'])
@cross_origin()
def hide_audio():
    try:
        if 'cover' not in request.files or 'secret' not in request.files:
            return {"error": "Both cover and secret audio required"}, 400
            
        cover = request.files['cover']
        secret = request.files['secret']
        
        # Save temporarily
        cover_path = os.path.join('uploads', cover.filename)
        secret_path = os.path.join('uploads', secret.filename)
        cover.save(cover_path)
        secret.save(secret_path)
        
        # Read audio files
        cover_rate, cover_data = wavfile.read(cover_path)
        secret_rate, secret_data = wavfile.read(secret_path)
        
        # Convert to mono if needed
        if len(cover_data.shape) > 1: cover_data = cover_data[:, 0]
        if len(secret_data.shape) > 1: secret_data = secret_data[:, 0]
        
        # Match lengths
        min_length = min(len(cover_data), len(secret_data))
        cover_data = cover_data[:min_length]
        secret_data = secret_data[:min_length]
        
        # Hide in 4 LSBs
        stego_data = (cover_data & 0xFFF0) | ((secret_data >> 12) & 0x000F)
        
        # Save result
        output_path = os.path.join('output', 'stego.wav')
        wavfile.write(output_path, cover_rate, stego_data)
        
        return send_file(output_path, mimetype='audio/wav')
        
    except Exception as e:
        return {"error": str(e)}, 500