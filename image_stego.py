from flask import Blueprint, request, send_file
from flask_cors import cross_origin
import cv2
import numpy as np
import os

image_routes = Blueprint('image_routes', __name__)

@image_routes.route('/hide_image', methods=['POST'])
@cross_origin()
def hide_image():
    try:
        if 'cover' not in request.files or 'secret' not in request.files:
            return {"error": "Both cover and secret images required"}, 400
            
        cover = request.files['cover']
        secret = request.files['secret']
        
        # Save temporarily
        cover_path = os.path.join('uploads', cover.filename)
        secret_path = os.path.join('uploads', secret.filename)
        cover.save(cover_path)
        secret.save(secret_path)
        
        # Process images
        cover_img = cv2.imread(cover_path)
        secret_img = cv2.imread(secret_path)
        
        # Resize secret to match cover
        secret_img = cv2.resize(secret_img, (cover_img.shape[1], cover_img.shape[0]))
        
        # Hide in LSBs
        stego_img = (cover_img & 0xFE) | (secret_img >> 7)
        
        # Save result
        output_path = os.path.join('output', 'stego.png')
        cv2.imwrite(output_path, stego_img)
        
        return send_file(output_path, mimetype='image/png')
        
    except Exception as e:
       return {"error": str(e)}, 500