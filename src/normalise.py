import os
from PIL import Image
import argparse

parser = argparse.ArgumentParser(
                    prog='normalise.py',
                    description='Script for normalizing the aspect ratio of flag images')
parser.add_argument('mode', choices=['pride', 'country'], help='Mode to run the script in')

args = parser.parse_args()

target_folder = 'pride_flags' if args.mode == 'pride' else 'country_flags'
target_width = 1153
target_height = 692
target_ratio = target_width / target_height

def upscale_image(img, target_width, target_height):
    width, height = img.size
    img_aspect = width / height
    target_aspect = target_width / target_height

    if img_aspect > target_aspect:
        # Image is wider than target, so scale based on height
        new_height = target_height
        new_width = int(new_height * img_aspect)
    else:
        # Image is taller than target, so scale based on width
        new_width = target_width
        new_height = int(new_width / img_aspect)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    new_img = Image.new("RGB", (target_width, target_height), (255, 255, 255))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    new_img.paste(resized_img, (paste_x, paste_y))

    return new_img

def normalize_aspect_ratio(target_folder, target_width, target_height):
    for filename in os.listdir(target_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            input_path = os.path.join(target_folder, filename)
            
            with Image.open(input_path) as img:
                width, height = img.size
                current_ratio = width / height

                if current_ratio == target_ratio:
                    # Skip images that already have the target aspect ratio
                    print(f"Skipping {filename} - already at target aspect ratio.")
                    continue
                else:
                    print(f"Normalizing aspect ratio for {filename}...")

                new_img = upscale_image(img, target_width, target_height)

            output_path = os.path.join(target_folder, f"normalized_{filename}")
            new_img.save(output_path)
            print(f"Saved normalized image as normalized_{filename}")

    print("Aspect ratio normalization and upscaling complete.")

if __name__ == "__main__":
    normalize_aspect_ratio(target_folder, target_width, target_height)