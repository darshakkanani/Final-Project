#!/usr/bin/env python3
"""
Hair Removal Model for Image Processing
Uses computer vision techniques to detect and remove hair artifacts from images
"""

import cv2
import numpy as np
from PIL import Image
import os
import logging
from skimage import morphology, filters
from scipy import ndimage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HairRemovalModel:
    """Advanced hair removal model using computer vision techniques"""
    
    def __init__(self):
        """Initialize the hair removal model"""
        logger.info("Hair removal model initialized")
        
        # Morphological kernels for different hair types
        self.thin_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.thick_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.line_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9))
        
    def remove_hair(self, input_path, output_path=None):
        """
        Remove hair from image using advanced computer vision techniques
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image (optional)
            
        Returns:
            tuple: (success, output_path, processing_info)
        """
        try:
            # Load image
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Image not found: {input_path}")
            
            # Read image
            image = cv2.imread(input_path)
            if image is None:
                raise ValueError("Could not load image")
                
            original_image = image.copy()
            logger.info(f"Processing image for hair removal: {image.shape}")
            
            # Apply hair removal pipeline
            processed_image = self._hair_removal_pipeline(image)
            
            # Generate output path if not provided
            if output_path is None:
                base, ext = os.path.splitext(input_path)
                output_path = f"{base}_hair_removed{ext}"
            
            # Save processed image
            cv2.imwrite(output_path, processed_image)
            
            # Calculate processing info
            processing_info = self._calculate_processing_info(original_image, processed_image)
            
            logger.info(f"Hair removal completed: {output_path}")
            return True, output_path, processing_info
            
        except Exception as e:
            logger.error(f"Error in hair removal: {e}")
            return False, None, {"error": str(e)}
    
    def _hair_removal_pipeline(self, image):
        """Complete hair removal pipeline"""
        
        # Step 1: Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Detect hair using multiple methods
        hair_mask = self._detect_hair_comprehensive(gray)
        
        # Step 3: Refine hair mask
        refined_mask = self._refine_hair_mask(hair_mask)
        
        # Step 4: Inpaint hair regions
        result = self._inpaint_hair_regions(image, refined_mask)
        
        # Step 5: Post-processing for natural look
        final_result = self._post_process_result(result, image)
        
        return final_result
    
    def _detect_hair_comprehensive(self, gray):
        """Comprehensive hair detection using multiple techniques"""
        
        # Method 1: Black hat morphological operation
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, self.thick_kernel)
        
        # Method 2: Top hat for bright hair
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, self.thick_kernel)
        
        # Method 3: Directional filtering for hair-like structures
        directional_mask = self._directional_hair_detection(gray)
        
        # Method 4: Edge-based detection
        edges = cv2.Canny(gray, 50, 150)
        edge_mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, self.thin_kernel)
        
        # Combine all methods
        combined_mask = cv2.bitwise_or(blackhat, tophat)
        combined_mask = cv2.bitwise_or(combined_mask, directional_mask)
        combined_mask = cv2.bitwise_or(combined_mask, edge_mask)
        
        # Threshold to binary
        _, binary_mask = cv2.threshold(combined_mask, 10, 255, cv2.THRESH_BINARY)
        
        return binary_mask
    
    def _directional_hair_detection(self, gray):
        """Detect hair using directional filters"""
        
        # Create directional kernels
        kernel_0 = np.array([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], dtype=np.float32)
        kernel_45 = np.array([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], dtype=np.float32)
        kernel_90 = np.array([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], dtype=np.float32)
        kernel_135 = np.array([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], dtype=np.float32)
        
        # Apply directional filters
        response_0 = cv2.filter2D(gray, -1, kernel_0)
        response_45 = cv2.filter2D(gray, -1, kernel_45)
        response_90 = cv2.filter2D(gray, -1, kernel_90)
        response_135 = cv2.filter2D(gray, -1, kernel_135)
        
        # Take maximum response
        max_response = np.maximum(np.maximum(response_0, response_45), 
                                 np.maximum(response_90, response_135))
        
        # Threshold
        _, directional_mask = cv2.threshold(max_response, 30, 255, cv2.THRESH_BINARY)
        
        return directional_mask.astype(np.uint8)
    
    def _refine_hair_mask(self, hair_mask):
        """Refine hair mask to reduce false positives"""
        
        # Remove small noise
        hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_OPEN, self.thin_kernel)
        
        # Fill small gaps in hair strands
        hair_mask = cv2.morphologyEx(hair_mask, cv2.MORPH_CLOSE, self.thin_kernel)
        
        # Remove very small components
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(hair_mask)
        refined_mask = np.zeros_like(hair_mask)
        
        for i in range(1, num_labels):  # Skip background (label 0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 10:  # Keep components larger than 10 pixels
                refined_mask[labels == i] = 255
        
        # Dilate slightly to ensure complete coverage
        refined_mask = cv2.dilate(refined_mask, self.thin_kernel, iterations=1)
        
        return refined_mask
    
    def _inpaint_hair_regions(self, image, mask):
        """Inpaint hair regions using advanced techniques"""
        
        # Use Navier-Stokes based inpainting for natural results
        inpainted = cv2.inpaint(image, mask, 3, cv2.INPAINT_NS)
        
        # Also try Fast Marching Method for comparison
        inpainted_fm = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
        
        # Blend both results for best quality
        alpha = 0.7
        blended = cv2.addWeighted(inpainted, alpha, inpainted_fm, 1-alpha, 0)
        
        return blended
    
    def _post_process_result(self, result, original):
        """Post-process result for natural appearance"""
        
        # Apply slight Gaussian blur to smooth inpainted regions
        smoothed = cv2.GaussianBlur(result, (3, 3), 0.5)
        
        # Blend with original to maintain natural texture
        alpha = 0.85
        final_result = cv2.addWeighted(smoothed, alpha, original, 1-alpha, 0)
        
        # Enhance local contrast
        lab = cv2.cvtColor(final_result, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge and convert back
        enhanced = cv2.merge([l, a, b])
        final_result = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return final_result
    
    def _calculate_processing_info(self, original, processed):
        """Calculate processing statistics"""
        
        # Calculate difference
        diff = cv2.absdiff(original, processed)
        mean_diff = np.mean(diff)
        
        # Calculate processing quality metrics
        mse = np.mean((original.astype(float) - processed.astype(float)) ** 2)
        psnr = 20 * np.log10(255.0 / np.sqrt(mse)) if mse > 0 else float('inf')
        
        return {
            "mean_difference": float(mean_diff),
            "psnr": float(psnr),
            "processing_quality": "High" if psnr > 30 else "Medium" if psnr > 25 else "Low"
        }
    
    def process_for_web(self, input_path, output_path=None):
        """
        Web-optimized hair removal processing
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            
        Returns:
            tuple: (success, output_path, info)
        """
        return self.remove_hair(input_path, output_path)

def remove_hair_from_image(input_path, output_path=None):
    """
    Convenience function for hair removal
    
    Args:
        input_path: Path to input image
        output_path: Path to save processed image
        
    Returns:
        tuple: (success, output_path, processing_info)
    """
    model = HairRemovalModel()
    return model.remove_hair(input_path, output_path)

if __name__ == "__main__":
    # Test the hair removal model
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        success, output_path, info = remove_hair_from_image(input_file)
        
        if success:
            print(f"✅ Hair removal completed")
            print(f"📁 Output: {output_path}")
            print(f"📊 Quality: {info.get('processing_quality', 'Unknown')}")
            print(f"📈 PSNR: {info.get('psnr', 0):.2f} dB")
        else:
            print("❌ Hair removal failed")
            print(f"Error: {info.get('error', 'Unknown error')}")
    else:
        print("Usage: python3 hair_removal.py <image_path>")
