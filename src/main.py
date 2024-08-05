import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

FOLDER_PATH = "flags"

def resize_image(image, target_size):
    """Resize and adjust the image to the target size.
    This should be done by normalise.py but is included here just in case.
    """
    aspect_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    if aspect_ratio > target_ratio:
        # Image is wider, scale based on width
        new_width = target_size[0]
        new_height = int(new_width / aspect_ratio)
    else:
        # Image is taller, scale based on height
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    # Create a new image with the target size and paste the resized image
    new_image = Image.new("RGB", target_size, (0, 0, 0))
    paste_x = (target_size[0] - new_width) // 2
    paste_y = (target_size[1] - new_height) // 2
    new_image.paste(image, (paste_x, paste_y))

    return new_image

def process_batch(image_files, folder_path, target_size, start_idx, end_idx):
    batch_sum = np.zeros((target_size[1], target_size[0], 3), dtype=np.float64)
    for filename in image_files[start_idx:end_idx]:
        image_path = os.path.join(folder_path, filename)
        with Image.open(image_path) as img:
            img = resize_image(img, target_size)
            img_array = np.array(img, dtype=np.float64)
            batch_sum += img_array
    return batch_sum

def create_mean_image(folder_path, sample_size=50):
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    first_image = Image.open(os.path.join(folder_path, image_files[0]))
    target_size = first_image.size
    
    total_images = len(image_files)
    total_sum = np.zeros((target_size[1], target_size[0], 3), dtype=np.float64)
    
    for start_idx in range(0, total_images, sample_size):
        end_idx = min(start_idx + sample_size, total_images)
        batch_sum = process_batch(image_files, folder_path, target_size, start_idx, end_idx)
        total_sum += batch_sum
        
        intermediate_mean = (total_sum / (end_idx)).astype(np.uint8)
        intermediate_image = Image.fromarray(intermediate_mean)
        intermediate_image.save(f"mean_image_interim_{end_idx}.jpg")
        print(f"Interim mean image saved for {end_idx} images.")
    
    # Calculate the final mean image
    final_mean = (total_sum / total_images).astype(np.uint8)
    final_image = Image.fromarray(final_mean)

    new_height = final_image.height + 150  # Increased white space to 150 pixels
    labeled_image = Image.new("RGB", (final_image.width, new_height), (255, 255, 255))
    labeled_image.paste(final_image, (0, 150))  # Paste the mean image below the white space

    draw = ImageDraw.Draw(labeled_image)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        subtitle_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # Fallback to default font if Arial is not available
        title_font = ImageFont.load_default().font_variant(size=36)
        subtitle_font = ImageFont.load_default().font_variant(size=24)

    title = "The average pride flag"
    subtitle1 = f"Generated from the mean of {total_images} images"
    subtitle2 = "Using pixel-wise averaging"

    def get_text_dimensions(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    title_width, title_height = get_text_dimensions(title, title_font)
    subtitle1_width, subtitle1_height = get_text_dimensions(subtitle1, subtitle_font)
    subtitle2_width, subtitle2_height = get_text_dimensions(subtitle2, subtitle_font)

    draw.text(((labeled_image.width - title_width) // 2, 20), title, fill=(0, 0, 0), font=title_font)
    draw.text(((labeled_image.width - subtitle1_width) // 2, 70), subtitle1, fill=(0, 0, 0), font=subtitle_font)
    draw.text(((labeled_image.width - subtitle2_width) // 2, 105), subtitle2, fill=(0, 0, 0), font=subtitle_font)

    # Save the final labeled image
    labeled_image.save("mean_image_final_labeled.jpg")
    print("Final labeled mean image saved as 'mean_image_final_labeled.jpg'.")

def main():
    create_mean_image(FOLDER_PATH, sample_size=200)

if __name__ == "__main__":
    main()