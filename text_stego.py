from flask import Blueprint, request, jsonify, render_template
from flask_cors import cross_origin
import binascii

text_routes = Blueprint('text_routes', __name__)

STEGO_DICT = {
    "the": ["our", "their"],
    "and": ["plus", "along with"],
    "to": ["towards", "until"],
    "of": ["belonging to", "from"],
    "a": ["one", "any"],
    "in": ["within", "inside"],
    "is": ["appears", "seems"],
    "it": ["this", "that"],
    "you": ["one", "they"],
    "that": ["which", "whom"]
}

def text_to_binary(text):
    """Convert text to binary with UTF-8 encoding"""
    binary = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:]
    return binary.zfill(8 * ((len(binary) + 7) // 8))

def binary_to_text(binary):
    """Convert binary string back to text"""
    n = int(binary, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode('utf-8')

def encode_in_cover(cover_text, secret_text):
    """Encode secret message into cover text"""
    secret_bin = text_to_binary(secret_text)
    words = cover_text.split()
    secret_ptr = 0
    
    for i in range(len(words)):
        if secret_ptr >= len(secret_bin):
            break
        word = words[i].lower()
        if word in STEGO_DICT:
            variation = int(secret_bin[secret_ptr])
            words[i] = STEGO_DICT[word][variation]
            secret_ptr += 1

    if secret_ptr < len(secret_bin):
        raise ValueError(f"Need {len(secret_bin)-secret_ptr} more substitutable words")
        
    return ' '.join(words)

def decode_from_cover(stego_text):
    """Decode message from stego text"""
    words = stego_text.split()
    binary_str = []
    
    for word in words:
        base_word = next((k for k, v in STEGO_DICT.items() if word.lower() in v), None)
        if base_word:
            binary_str.append(str(STEGO_DICT[base_word].index(word.lower())))
    
    return binary_to_text(''.join(binary_str))

@text_routes.route('/')
def text_interface():
    return render_template('text.html')

@text_routes.route('/process_text', methods=['POST'])
@cross_origin()
def process_text():
    try:
        data = request.get_json()
        action = data.get('action', 'encode').lower()

        if action == 'encode':
            cover_text = data.get('cover_text', '')
            secret_text = data.get('secret_text', '')
            
            if not cover_text or not secret_text:
                return jsonify({"error": "Both fields required", "status": "error"}), 400

            encoded_text = encode_in_cover(cover_text, secret_text)
            return jsonify({
                "status": "success",
                "encoded_text": encoded_text,
                "original_text": secret_text
            })

        elif action == 'decode':
            stego_text = data.get('stego_text', '')
            if not stego_text:
                return jsonify({"error": "Stego text required", "status": "error"}), 400

            decoded_text = decode_from_cover(stego_text)
            return jsonify({
                "status": "success",
                "decoded_secret": decoded_text
            })

        return jsonify({"error": "Invalid action", "status": "error"}), 400

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 400