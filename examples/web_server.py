"""Example web service for ZPLConvert."""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from zplconvert import convert_zpl_to_image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

@app.route('/')
def index():
    """Serve the test page."""
    return send_from_directory(os.path.dirname(__file__), 'test_page.html')

@app.route('/convert', methods=['POST'])
def convert():
    """Endpoint to convert ZPL to PNG."""
    if request.is_json:
        zpl_data = request.json.get('zpl')
    else:
        zpl_data = request.form.get('zpl')
    
    if not zpl_data:
        return jsonify({'error': 'No ZPL data provided'}), 400
    
    try:
        # Convert ZPL to an image
        image = convert_zpl_to_image(zpl_data)
        image_path = 'output.png'
        image.save(image_path)
        return jsonify({'message': 'Conversion successful', 'image_path': image_path})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during conversion: {str(e)}")
        print(error_details)
        return jsonify({
            'error': str(e),
            'details': error_details
        }), 500

@app.route('/output.png')
def serve_image():
    """Serve the generated image."""
    return send_from_directory(os.getcwd(), 'output.png')

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify the server is running."""
    return jsonify({'message': 'Test endpoint is working!'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
