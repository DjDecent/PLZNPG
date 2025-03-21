"""Example web service for ZPLConvert."""

import sys
import os
import time
import io
from contextlib import redirect_stdout, redirect_stderr

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
        # Capture both stdout and stderr
        log_output = io.StringIO()
        stderr_output = io.StringIO()
        
        # Print some initial log messages to verify logging
        print("Starting ZPL conversion process...")
        print(f"ZPL data length: {len(zpl_data)} characters")
        
        start_time = time.time()
        
        # Capture both stdout and stderr during conversion
        with redirect_stdout(log_output), redirect_stderr(stderr_output):
            # Convert ZPL to an image with optimized parameters
            image = convert_zpl_to_image(zpl_data, optimize=True)
            print("Conversion completed successfully")
            
        end_time = time.time()
        processing_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        print(f"Processing time: {processing_time}ms")
        
        # Use BytesIO to avoid disk I/O
        image_data = io.BytesIO()
        image.save(image_data, format='PNG', optimize=True)
        image_data.seek(0)
        
        # Save physical file with reduced quality for faster rendering
        image_path = 'output.png'
        image.save(image_path, optimize=True)
        print(f"Image saved as {image_path}")
        
        # Get captured logs (combine stdout and stderr)
        logs = log_output.getvalue()
        stderr_logs = stderr_output.getvalue()
        
        # Check if logs are empty and add a fallback message
        if not logs.strip():
            logs = "No detailed logs were generated during conversion.\n"
        
        # Add stderr logs if any
        if stderr_logs.strip():
            logs += "\nErrors/Warnings:\n" + stderr_logs
            
        # Add system info to the logs
        logs += f"\nServer info: Python {sys.version.split()[0]}"
        
        return jsonify({
            'message': 'Conversion successful', 
            'image_path': image_path,
            'logs': logs,
            'processing_time': processing_time,
            'optimized': True  # Flag to indicate optimization was applied
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during conversion: {str(e)}")
        print(error_details)
        return jsonify({
            'error': str(e),
            'details': error_details,
            'logs': f"Error during conversion: {str(e)}\n\n{error_details}"
        }), 500

# Add a new caching endpoint for frequently used labels
@app.route('/cached_convert', methods=['POST'])
def cached_convert():
    """Endpoint to convert ZPL with caching for repeated requests."""
    if request.is_json:
        zpl_data = request.json.get('zpl')
        cache_key = request.json.get('cache_key', '')
    else:
        zpl_data = request.form.get('zpl')
        cache_key = request.form.get('cache_key', '')
    
    # Simple in-memory cache using cache_key or hash of ZPL content
    import hashlib
    if not cache_key:
        cache_key = hashlib.md5(zpl_data.encode()).hexdigest()
        
    # Check if we have this in cache (would need to implement persistence for production)
    cache_path = f"cache/{cache_key}.png"
    if os.path.exists(cache_path):
        return jsonify({
            'message': 'Retrieved from cache', 
            'image_path': cache_path,
            'logs': 'Image served from cache',
            'processing_time': 0,
            'cached': True
        })
    
    # If not in cache, process normally and then cache
    try:
        # Capture both stdout and stderr
        log_output = io.StringIO()
        stderr_output = io.StringIO()
        
        # Print some initial log messages to verify logging
        print("Starting ZPL conversion process...")
        print(f"ZPL data length: {len(zpl_data)} characters")
        
        start_time = time.time()
        
        # Capture both stdout and stderr during conversion
        with redirect_stdout(log_output), redirect_stderr(stderr_output):
            # Convert ZPL to an image with optimized parameters
            image = convert_zpl_to_image(zpl_data, optimize=True)
            print("Conversion completed successfully")
            
        end_time = time.time()
        processing_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        print(f"Processing time: {processing_time}ms")
        
        # Use BytesIO to avoid disk I/O
        image_data = io.BytesIO()
        image.save(image_data, format='PNG', optimize=True)
        image_data.seek(0)
        
        # Save physical file with reduced quality for faster rendering
        image.save(cache_path, optimize=True)
        print(f"Image saved as {cache_path}")
        
        # Get captured logs (combine stdout and stderr)
        logs = log_output.getvalue()
        stderr_logs = stderr_output.getvalue()
        
        # Check if logs are empty and add a fallback message
        if not logs.strip():
            logs = "No detailed logs were generated during conversion.\n"
        
        # Add stderr logs if any
        if stderr_logs.strip():
            logs += "\nErrors/Warnings:\n" + stderr_logs
            
        # Add system info to the logs
        logs += f"\nServer info: Python {sys.version.split()[0]}"
        
        return jsonify({
            'message': 'Conversion successful', 
            'image_path': cache_path,
            'logs': 'Image was processed and cached for future use',
            'processing_time': processing_time
        })
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error during conversion: {str(e)}")
        print(error_details)
        return jsonify({
            'error': str(e),
            'details': error_details,
            'logs': f"Error during conversion: {str(e)}\n\n{error_details}"
        }), 500

@app.route('/output.png')
def serve_image():
    """Serve the generated image."""
    return send_from_directory(os.getcwd(), 'output.png')

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Test endpoint to verify the server is running."""
    # Capture system information for the test endpoint
    import platform
    import sys
    import psutil  # You might need to add this to requirements.txt
    
    logs = io.StringIO()
    logs.write("Server test information:\n")
    logs.write(f"Python version: {sys.version}\n")
    logs.write(f"Platform: {platform.platform()}\n")
    logs.write(f"OS: {platform.system()} {platform.release()}\n")
    
    # Add more detailed system info if psutil is available
    try:
        logs.write(f"\nMemory usage: {psutil.virtual_memory().percent}%\n")
        logs.write(f"CPU usage: {psutil.cpu_percent(interval=0.1)}%\n")
    except (ImportError, NameError):
        logs.write("\n(Install psutil for additional system metrics)\n")
    
    # Test log capturing to verify it works
    print("Test endpoint was called")
    
    return jsonify({
        'message': 'Shut up, the server is working!',
        'logs': logs.getvalue(),
        'processing_time': 0  # Zero indicates this is just a test
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
