import cv2
import os
import numpy as np

def sketch_style(input_directory, output_directory):
    """
    Transform images in the input directory into sketch-style images and save them in the output directory.
    
    Args:
        input_directory (str): Path to the directory containing input images.
        output_directory (str): Path to the directory to save the transformed images.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)

            # Load the image
            image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

            # Check if the image was loaded correctly
            if image is None:
                print(f"Failed to load image: {input_path}. Skipping...")
                continue

            try:
                # Apply a Gaussian blur to reduce noise
                blurred = cv2.GaussianBlur(image, (5, 5), 0)

                # Detect edges using the Canny algorithm
                edges = cv2.Canny(blurred, 50, 150)

                # Invert the colors (white background, black lines)
                inverted = cv2.bitwise_not(edges)

                # Apply adaptive thresholding for smoothing the sketch lines
                smoothed = cv2.adaptiveThreshold(
                    inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY, 9, 2
                )

                # Save the stylized image
                cv2.imwrite(output_path, smoothed)
                print(f"Processed: {filename} -> {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

# Paths to the input and output directories
input_directory = "data/original_engraving/"
output_directory = "data/sketchStyle_traced_engraving/"

# Apply the sketch transformation
sketch_style(input_directory, output_directory)
