"""
Image Resizer and Hair Removal Web Application
Features:
- Image upload and processing
- Smart image resizing (380x380)
- Advanced hair removal using computer vision
- Quality preservation
- Multiple format support
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import time

# Import our image processing modules from AI folder
from AI.image_resizer import WebAppImageResizer
from AI.hair_removal import HairRemovalModel

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESIZED_FOLDER'] = 'resized'
app.config['PROCESSED_FOLDER'] = 'processed'

# Create directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESIZED_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)

# Initialize image processing models
image_resizer = WebAppImageResizer(target_size=(380, 380))
hair_removal_model = HairRemovalModel()

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
            
            # Step 1: Resize the uploaded image
            resized_filename = f"resized_{filename}"
            resized_path = os.path.join(app.config['RESIZED_FOLDER'], resized_filename)
            
            resize_success, _, original_size, new_size = image_resizer.resize_image(
                upload_path, 
                resized_path, 
                enhance=True
            )
            
            if not resize_success:
                return jsonify({'error': 'Failed to resize image'})
            
            # Step 2: Apply hair removal to the resized image
            processed_filename = f"hair_removed_{filename}"
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
            
            hair_removal_success, _, processing_info = hair_removal_model.process_for_web(
                resized_path,
                processed_path
            )
            
            if not hair_removal_success:
                return jsonify({'error': 'Failed to remove hair from image'})
            
            return jsonify({
                'success': True,
                'original_image': f'/uploads/{filename}',
                'resized_image': f'/resized/{resized_filename}',
                'processed_image': f'/processed/{processed_filename}',
                'original_size': f"{original_size[0]}x{original_size[1]}",
                'resized_size': f"{new_size[0]}x{new_size[1]}",
                'processing_quality': processing_info.get('processing_quality', 'Unknown'),
                'psnr': processing_info.get('psnr', 0)
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

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    print("Image Resizer & Hair Removal Web Application")
    print("=" * 50)
    print("Features:")
    print("   • Smart Image Resizing (380x380)")
    print("   • Advanced Hair Removal using Computer Vision")
    print("   • Quality Preservation")
    print("   • Multiple Format Support")
    print("=" * 50)
    print("Starting server...")
    print("Open your browser and go to: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5001)
