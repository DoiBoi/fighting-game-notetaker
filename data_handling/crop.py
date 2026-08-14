import os

from PIL import Image


def batch_crop_images(input_folder, output_folder, crop_box):
    """
    Crops all images in a folder and saves them to a new folder.

    :param input_folder: Path to the folder containing original images.
    :param output_folder: Path to save the cropped images.
    :param crop_box: A tuple of 4 coordinates: (left, upper, right, lower)
    """
    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Supported image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, f"cropped_{filename}")

            try:
                with Image.open(input_path) as img:
                    # Perform the crop
                    cropped_img = img.crop(crop_box)

                    # Save the cropped image
                    cropped_img.save(output_path)
                    print(f"Successfully cropped: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

# --- Configuration ---
# Define your box dimensions: (left, upper, right, lower)
# Example: Crops a 400x400 box starting at X=100, Y=100
BOX_TO_CROP = (0, 23, 197, 97)

INPUT_DIR = "./sf6_characters"
OUTPUT_DIR = "./templates/characters"

# Run the function
batch_crop_images(INPUT_DIR, OUTPUT_DIR, BOX_TO_CROP)
