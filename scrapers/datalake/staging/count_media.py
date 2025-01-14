import os

def count_images_in_folder(folder_path):
    # List of common image file extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

    # Count the number of image files
    image_count = 0
    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_count += 1

    return image_count

if __name__ == "__main__":
    media_folder_path = "C:/Users/antoi/Documents/Projets/Projet Certif/EngraveDetect/scrapers/datalake/staging/media"
    image_count = count_images_in_folder(media_folder_path)
    print(f"Number of images in the folder '{media_folder_path}': {image_count}")