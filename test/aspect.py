import os
from PIL import Image
from collections import defaultdict

def get_aspect_ratio(width, height):
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    divisor = gcd(width, height)
    return f"{width // divisor}:{height // divisor}"

def print_unique_aspect_ratios(folder_path):
    aspect_ratios = defaultdict(list)
    
    for filename in os.listdir(folder_path):
        try:
            with Image.open(os.path.join(folder_path, filename)) as img:
                width, height = img.size
                ratio = get_aspect_ratio(width, height)
                aspect_ratios[ratio].append(filename)
        except IOError:
            print(f"Error opening {filename}")
    
    for ratio, files in aspect_ratios.items():
        print(f"Aspect Ratio {ratio} - {len(files)}")
        print()

folder_path = "flags"
print_unique_aspect_ratios(folder_path)