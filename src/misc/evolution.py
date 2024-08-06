import os
from PIL import Image, ImageDraw, ImageFont
import argparse

parser = argparse.ArgumentParser(
                    prog='gather.py',
                    description='Script for downloading flag images from a GitHub repository')
parser.add_argument('mode', choices=['pride', 'country'], help='Mode to run the script in')

args = parser.parse_args()

def create_evolution_image(image_paths, output_path, scale_factor=0.25):
    # Load and scale images
    images = []
    for path in image_paths:
        img = Image.open(path)
        new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        images.append(img)
    
    # Calculate dimensions
    padding = 50  # Padding between images
    total_width = sum(img.width for img in images) + padding * (len(images) - 1)
    max_height = max(img.height for img in images)
    
    # Create a new image with white background
    result = Image.new('RGB', (total_width + 100, max_height + 200), color='white')
    
    # Paste images
    x_offset = 50  # Start with some left padding
    for i, img in enumerate(images):
        result.paste(img, (x_offset, 100))
        draw = ImageDraw.Draw(result)
        font = ImageFont.truetype("arial.ttf", 20)
        iteration = image_paths[i].split('/')[-1].split('_')[1].split('.')[0]
        if 'final' in iteration:
            label = "Final iteration"
        else:
            label = f"{iteration} iterations"
        text_width = draw.textlength(label, font=font)
        draw.text((x_offset + (img.width - text_width) / 2, 60), label, font=font, fill='black')
        
        if i < len(images) - 1:
            arrow_start = (x_offset + img.width + 10, max_height // 2 + 100)
            arrow_end = (arrow_start[0] + padding - 20, arrow_start[1])
            draw.line([arrow_start, arrow_end], fill='black', width=max(1, int(2 * scale_factor)))
            draw.polygon([arrow_end, (arrow_end[0] - 5, arrow_end[1] - 3), (arrow_end[0] - 5, arrow_end[1] + 3)], fill='black')
        
        x_offset += img.width + padding

    # Save the result
    result.save(output_path)
    print(f"Evolution image saved to {output_path}")

if args.mode == 'pride':
    image_paths = [
        'images/pride_10.jpg',
        'images/pride_30.jpg',
        'images/pride_60.jpg',
        'images/pride_200.jpg',
        'images/pride_600.jpg',
        'images/pride_final.jpg'
    ]
else:
    image_paths = [
        'images/country_10.jpg',
        'images/country_30.jpg',
        'images/country_60.jpg',
        'images/country_200.jpg',
        'images/country_400.jpg',
        'images/country_final.jpg'
    ]

# Create the evolution image
create_evolution_image(image_paths, f'{args.mode}_flag_evolution.jpg')