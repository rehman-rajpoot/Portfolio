# Images Folder

This folder contains all image assets for the portfolio website, in WebP format for optimal performance.

## Image Organization

- **profile/**: Profile pictures and avatars
- **projects/**: Project screenshots and previews
- **portfolio/**: General portfolio images
- **icons/**: Custom icons and graphics

## WebP Format

WebP images are used for better compression and faster loading times. You can convert your images to WebP using:
- Online tools: https://convertio.co/, https://cloudconvert.com/
- ImageMagick: `convert image.jpg image.webp`
- Pillow (Python): See script below

## Python Script to Convert Images to WebP

```python
from PIL import Image
import os

def convert_to_webp(input_folder, output_folder):
    """Convert all images to WebP format"""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + '.webp'
            output_path = os.path.join(output_folder, output_filename)
            
            try:
                img = Image.open(input_path)
                img.save(output_path, 'WEBP', quality=80)
                print(f"✓ Converted: {filename} → {output_filename}")
            except Exception as e:
                print(f"✗ Error converting {filename}: {e}")

# Usage
convert_to_webp('path/to/input', 'path/to/output')
```

## Usage in HTML

```html
<!-- Use WebP with fallback -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="Description">
</picture>
```

## Recommended Image Sizes

- Profile Images: 400x400px (1:1 aspect ratio)
- Project Thumbnails: 600x400px (3:2 aspect ratio)
- Hero Images: 1200x800px (3:2 aspect ratio)
- Icons: 64x64px or 128x128px
