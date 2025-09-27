"""
Image Resizer Web Application
Features:
- Image upload and processing
- Smart image resizing (380x380)
- Quality preservation
- Multiple format support
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import time

# Import our image resizing module from AI folder
from AI.image_resizer import WebAppImageResizer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESIZED_FOLDER'] = 'resized'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESIZED_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Initialize image resizer
image_resizer = WebAppImageResizer(target_size=(380, 380))

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    if file and allowed_file(file.filename):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Resize the uploaded image
            resized_filename = f"resized_{filename}"
            resized_path = os.path.join(app.config['RESIZED_FOLDER'], resized_filename)
            
            success, _, original_size, new_size = image_resizer.resize_image(
                upload_path, 
                resized_path, 
                enhance=True
            )
            
            if not success:
                return jsonify({'error': 'Failed to resize image'})
            
            return jsonify({
                'success': True,
                'original_image': f'/uploads/{filename}',
                'resized_image': f'/resized/{resized_filename}',
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'resized_size': f"{new_size[0]}x{new_size[1]}"
            })
            
        except Exception as e:
            return jsonify({'error': f'Processing failed: {str(e)}'})
    
    return jsonify({'error': 'Invalid file type'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/resized/<filename>')
def resized_file(filename):
    return send_from_directory(app.config['RESIZED_FOLDER'], filename)

if __name__ == '__main__':
    print("Image Resizer Web Application")
    print("=" * 40)
    print("Features:")
    print("   • Smart Image Resizing (380x380)")
    print("   • Quality Preservation")
    print("   • Multiple Format Support")
    print("=" * 40)
    print("Starting server...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 40)
    app.run(debug=True, host='0.0.0.0', port=5001)
