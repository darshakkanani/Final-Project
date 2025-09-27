#!/usr/bin/env python3
"""
Smart Image Resizer for GUISKIN Web Application
- Memory-efficient resizing
- Quality preservation
- Multiple target sizes support
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebAppImageResizer:
    """Smart image resizer optimized for web applications"""
    
    def __init__(self, target_size=(380, 380)):
        self.target_size = target_size
        logger.info(f"Image resizer initialized for {target_size}")
    
    def resize_image(self, input_path, output_path=None, enhance=True):
        """
        Resize image with smart quality preservation
        
        Args:
            input_path: Path to input image
            output_path: Path to save resized image (optional)
            enhance: Whether to apply smart enhancement
            
        Returns:
            tuple: (success, output_path, original_size, new_size)
        """
        try:
            # Load image
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Image not found: {input_path}")
            
            image = Image.open(input_path)
            original_size = image.size
            logger.info(f"Processing image: {original_size} -> {self.target_size}")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Smart resize
            resized_image = self._smart_resize(image)
            
            # Optional enhancement
            if enhance:
                resized_image = self._enhance_image(resized_image)
            
            # Generate output path if not provided
            if output_path is None:
                base, ext = os.path.splitext(input_path)
                output_path = f"{base}_resized{ext}"
            
            # Save with high quality
            resized_image.save(output_path, quality=95, optimize=True)
            
            logger.info(f"Image resized successfully: {output_path}")
            return True, output_path, original_size, self.target_size
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return False, None, None, None
    
    def _smart_resize(self, image):
        """Smart multi-step resizing for best quality"""
        original_size = image.size
        target_w, target_h = self.target_size
        
        # Convert to array for OpenCV processing
        img_array = np.array(image).astype(np.float32)
        
        # Smart interpolation method selection
        scale_factor = min(target_w / original_size[0], target_h / original_size[1])
        
        if scale_factor > 1.5:
            # Upscaling - use CUBIC for smoothness
            interpolation = cv2.INTER_CUBIC
        elif scale_factor < 0.5:
            # Heavy downscaling - use AREA for best quality
            interpolation = cv2.INTER_AREA
        else:
            # Normal scaling - use LANCZOS for sharpness
            interpolation = cv2.INTER_LANCZOS4
        
        # Multi-step resizing for large scale changes
        current_size = original_size
        current_img = img_array
        
        while True:
            # Calculate intermediate size
            scale_x = target_w / current_size[0]
            scale_y = target_h / current_size[1]
            
            # If we're close to target, resize directly
            if 0.5 <= min(scale_x, scale_y) <= 2.0:
                final_img = cv2.resize(current_img, self.target_size, interpolation=interpolation)
                break
            
            # Otherwise, resize by factor of 2
            if scale_x > 2 or scale_y > 2:
                # Upscale by 2x
                new_size = (current_size[0] * 2, current_size[1] * 2)
                current_img = cv2.resize(current_img, new_size, interpolation=cv2.INTER_CUBIC)
            else:
                # Downscale by 2x
                new_size = (current_size[0] // 2, current_size[1] // 2)
                current_img = cv2.resize(current_img, new_size, interpolation=cv2.INTER_AREA)
            
            current_size = new_size
        
        return Image.fromarray(np.clip(final_img, 0, 255).astype(np.uint8))
    
    def _enhance_image(self, image):
        """Smart enhancement based on image characteristics"""
        # Convert to array for analysis
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Analyze image characteristics
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        logger.info(f"Image analysis - Blur: {blur_score:.1f}, Brightness: {brightness:.1f}, Contrast: {contrast:.1f}")
        
        enhanced = image
        
        # Smart sharpening based on blur score
        if blur_score < 100:  # Image is blurry
            # Apply unsharp masking
            img_array = np.array(enhanced)
            gaussian = cv2.GaussianBlur(img_array, (0, 0), 1.0)
            sharpened = cv2.addWeighted(img_array, 1.5, gaussian, -0.5, 0)
            enhanced = Image.fromarray(np.clip(sharpened, 0, 255).astype(np.uint8))
            logger.info("Applied sharpening for blurry image")
        
        # Smart contrast adjustment
        if contrast < 30:  # Low contrast
            enhancer = ImageEnhance.Contrast(enhanced)
            enhanced = enhancer.enhance(1.2)
            logger.info("Enhanced contrast for flat image")
        
        # Smart brightness adjustment
        if brightness < 80:  # Too dark
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(1.1)
            logger.info("Brightened dark image")
        elif brightness > 200:  # Too bright
            enhancer = ImageEnhance.Brightness(enhanced)
            enhanced = enhancer.enhance(0.95)
            logger.info("Reduced brightness for overexposed image")
        
        return enhanced
    
    def resize_for_model(self, input_path, model_size=(224, 224)):
        """
        Resize image specifically for ML model input
        
        Args:
            input_path: Path to input image
            model_size: Target size for model (width, height)
            
        Returns:
            numpy array ready for model input
        """
        try:
            # Temporarily change target size
            original_target = self.target_size
            self.target_size = model_size
            
            # Load and resize
            image = Image.open(input_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            resized_image = self._smart_resize(image)
            
            # Convert to numpy array and normalize
            img_array = np.array(resized_image) / 255.0
            img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
            
            # Restore original target size
            self.target_size = original_target
            
            return img_array
            
        except Exception as e:
            logger.error(f"Error preparing image for model: {e}")
            # Restore original target size
            self.target_size = original_target
            return None

def preprocess_image_for_web(img_path, target_size=(380, 380)):
    """
    Convenience function for web app image preprocessing
    
    Args:
        img_path: Path to input image
        target_size: Target size (width, height)
        
    Returns:
        tuple: (success, resized_path, original_size, new_size)
    """
    resizer = WebAppImageResizer(target_size=target_size)
    return resizer.resize_image(img_path)

if __name__ == "__main__":
    # Test the resizer
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        success, output_path, orig_size, new_size = preprocess_image_for_web(input_file)
        
        if success:
            print(f"✅ Resized: {orig_size} -> {new_size}")
            print(f"📁 Output: {output_path}")
        else:
            print("❌ Resizing failed")
    else:
        print("Usage: python3 image_resizer.py <image_path>")
