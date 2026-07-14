"""
advanced_preprocess.py

Advanced image preprocessing techniques for challenging receipt images.

This module provides additional preprocessing methods beyond the standard
pipeline to handle:
- Low contrast/faded thermal receipts
- Uneven lighting
- Shadows and wrinkles
- Very small or large text
- Perspective distortion

Author: Kiro (Advanced Processing)
"""

import cv2
import numpy as np
from pathlib import Path


def adaptive_bilateral_denoise(image, intensity='medium'):
    """
    Apply adaptive bilateral filtering based on image noise level.
    Preserves edges while removing noise.
    
    Args:
        image: Grayscale image
        intensity: 'light', 'medium', 'heavy'
    
    Returns:
        Denoised image
    """
    # Estimate noise level
    noise_sigma = estimate_noise(image)
    
    if intensity == 'light' or noise_sigma < 5:
        d, sigmaColor, sigmaSpace = 5, 50, 50
    elif intensity == 'medium' or noise_sigma < 15:
        d, sigmaColor, sigmaSpace = 7, 75, 75
    else:  # heavy or noise_sigma >= 15
        d, sigmaColor, sigmaSpace = 9, 100, 100
    
    return cv2.bilateralFilter(image, d, sigmaColor, sigmaSpace)


def estimate_noise(image):
    """
    Estimate noise level in image using Laplacian variance method.
    Higher values indicate more noise.
    """
    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()


def enhance_faded_thermal_receipt(image):
    """
    Specifically enhance faded thermal receipt prints.
    
    Thermal receipts fade over time and have low contrast.
    This applies aggressive contrast enhancement.
    
    Args:
        image: Grayscale image
    
    Returns:
        Enhanced image
    """
    # Apply contrast stretching
    min_val, max_val = np.percentile(image, [2, 98])
    stretched = np.clip((image - min_val) * (255.0 / (max_val - min_val)), 0, 255).astype(np.uint8)
    
    # Apply aggressive CLAHE
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4))
    enhanced = clahe.apply(stretched)
    
    # Slight gamma correction to brighten
    gamma = 1.2
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    enhanced = cv2.LUT(enhanced, table)
    
    return enhanced


def remove_shadows_and_lighting(image):
    """
    Remove shadows and uneven lighting using morphological operations.
    Useful for receipts photographed under poor lighting.
    
    Args:
        image: Grayscale image
    
    Returns:
        Shadow-removed image
    """
    # Dilate to get background estimate
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    background = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    # Divide original by background to remove lighting variations
    normalized = cv2.divide(image, background, scale=255)
    
    return normalized


def perspective_correction(image, debug=False):
    """
    Correct perspective distortion in receipt images.
    Useful when receipt is photographed at an angle.
    
    Args:
        image: Color or grayscale image
        debug: If True, visualizes detected corners
    
    Returns:
        Perspective-corrected image
    """
    gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return image
    
    # Get largest contour (assume it's the receipt)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Approximate to polygon
    peri = cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
    
    # If we got 4 corners, apply perspective transform
    if len(approx) == 4:
        pts = approx.reshape(4, 2)
        rect = order_points(pts)
        
        # Calculate destination points
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")
        
        # Apply perspective transform
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    return image


def order_points(pts):
    """
    Order points in clockwise order: top-left, top-right, bottom-right, bottom-left
    """
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect


def sharpen_text(image, strength='medium'):
    """
    Sharpen text to improve OCR accuracy.
    Use carefully - over-sharpening can introduce artifacts.
    
    Args:
        image: Grayscale image
        strength: 'light', 'medium', 'heavy'
    
    Returns:
        Sharpened image
    """
    if strength == 'light':
        kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
    elif strength == 'medium':
        kernel = np.array([[0,-1,0], [-1, 5,-1], [0,-1,0]])
    else:  # heavy
        kernel = np.array([[-1,-1,-1,-1,-1],
                          [-1, 2, 2, 2,-1],
                          [-1, 2, 8, 2,-1],
                          [-1, 2, 2, 2,-1],
                          [-1,-1,-1,-1,-1]])
    
    sharpened = cv2.filter2D(image, -1, kernel)
    return sharpened


def remove_wrinkles_and_creases(image):
    """
    Reduce visibility of wrinkles and creases in crumpled receipts.
    
    Args:
        image: Grayscale image
    
    Returns:
        Smoothed image
    """
    # Use morphological closing to fill wrinkle lines
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    closed = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    
    # Blend with original to preserve text sharpness
    alpha = 0.7
    blended = cv2.addWeighted(image, alpha, closed, 1-alpha, 0)
    
    return blended


def auto_scale_for_ocr(image, target_dpi=300, current_dpi=72):
    """
    Scale image to optimal DPI for OCR (typically 300 DPI).
    
    Args:
        image: Input image
        target_dpi: Target DPI for OCR (default 300)
        current_dpi: Estimated current DPI (default 72)
    
    Returns:
        Scaled image
    """
    scale_factor = target_dpi / current_dpi
    
    if scale_factor != 1.0:
        height, width = image.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Use INTER_CUBIC for upscaling, INTER_AREA for downscaling
        interpolation = cv2.INTER_CUBIC if scale_factor > 1 else cv2.INTER_AREA
        scaled = cv2.resize(image, (new_width, new_height), interpolation=interpolation)
        return scaled
    
    return image


def preprocess_receipt_advanced(image_path, output_path=None, mode='auto'):
    """
    Advanced preprocessing pipeline with multiple enhancement modes.
    
    Args:
        image_path: Path to receipt image
        output_path: Optional path to save processed image
        mode: Preprocessing mode
            - 'auto': Automatically detect best approach
            - 'faded': For faded thermal receipts
            - 'shadow': For receipts with shadows/uneven lighting
            - 'wrinkled': For crumpled receipts
            - 'perspective': For angled photos
            - 'aggressive': All enhancements (may over-process)
    
    Returns:
        Processed image
    """
    from utils.preprocess import deskew  # Use existing deskew
    
    # Load image
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    # Step 1: Deskew (always do this first)
    image = deskew(image)
    
    # Step 2: Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Step 3: Mode-specific processing
    if mode == 'auto':
        # Automatically detect image issues
        noise_level = estimate_noise(gray)
        mean_intensity = np.mean(gray)
        
        # Low contrast (faded thermal receipt)
        if mean_intensity > 200 or (np.max(gray) - np.min(gray)) < 100:
            gray = enhance_faded_thermal_receipt(gray)
        
        # High noise
        if noise_level > 10:
            gray = adaptive_bilateral_denoise(gray, 'medium')
        
        # Uneven lighting
        std_by_region = np.std([np.std(gray[i:i+50, j:j+50]) 
                                for i in range(0, gray.shape[0]-50, 50) 
                                for j in range(0, gray.shape[1]-50, 50)])
        if std_by_region > 20:
            gray = remove_shadows_and_lighting(gray)
    
    elif mode == 'faded':
        gray = enhance_faded_thermal_receipt(gray)
        gray = adaptive_bilateral_denoise(gray, 'light')
    
    elif mode == 'shadow':
        gray = remove_shadows_and_lighting(gray)
        gray = adaptive_bilateral_denoise(gray, 'medium')
    
    elif mode == 'wrinkled':
        gray = remove_wrinkles_and_creases(gray)
        gray = adaptive_bilateral_denoise(gray, 'light')
    
    elif mode == 'perspective':
        image = perspective_correction(image)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    elif mode == 'aggressive':
        gray = enhance_faded_thermal_receipt(gray)
        gray = remove_shadows_and_lighting(gray)
        gray = remove_wrinkles_and_creases(gray)
        gray = adaptive_bilateral_denoise(gray, 'heavy')
    
    # Step 4: Scale to optimal DPI (300)
    gray = auto_scale_for_ocr(gray, target_dpi=300, current_dpi=72)
    
    # Step 5: Denoise (if not already done)
    if mode not in ['faded', 'shadow', 'wrinkled', 'aggressive']:
        gray = cv2.fastNlMeansDenoising(gray, h=7)
    
    # Step 6: CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    processed = clahe.apply(gray)
    
    # Step 7: Optional sharpening for very small text
    # Uncomment if needed:
    # processed = sharpen_text(processed, 'light')
    
    # Save if output path provided
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), processed)
    
    return processed


# Convenience functions for specific issues
def preprocess_faded_receipt(image_path, output_path=None):
    """Quick preprocessing for faded thermal receipts."""
    return preprocess_receipt_advanced(image_path, output_path, mode='faded')


def preprocess_shadowed_receipt(image_path, output_path=None):
    """Quick preprocessing for receipts with shadows."""
    return preprocess_receipt_advanced(image_path, output_path, mode='shadow')


def preprocess_wrinkled_receipt(image_path, output_path=None):
    """Quick preprocessing for crumpled receipts."""
    return preprocess_receipt_advanced(image_path, output_path, mode='wrinkled')


if __name__ == "__main__":
    # Test the preprocessing
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_preprocess.py <image_path> [mode]")
        print("Modes: auto, faded, shadow, wrinkled, perspective, aggressive")
        sys.exit(1)
    
    image_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'auto'
    
    output_path = f"preprocessed_{mode}_{Path(image_path).name}"
    
    print(f"Processing {image_path} in '{mode}' mode...")
    processed = preprocess_receipt_advanced(image_path, output_path, mode=mode)
    print(f"Saved to {output_path}")
    print(f"Image size: {processed.shape}")
