from PIL import Image, ImageDraw
import os

def generate_icon(size):
    """Generate a coffee leaf icon in memory"""
    img = Image.new('RGBA', (size, size), (46, 204, 113, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple leaf shape
    center = size // 2
    width = size // 3
    height = size // 2
    
    # Leaf path
    points = [
        (center, center - height//2),
        (center + width, center),
        (center, center + height//2),
        (center - width, center)
    ]
    
    draw.polygon(points, fill=(46, 204, 113, 255))
    draw.line([(center, center - height//2), (center, center + height//2)], fill=(39, 174, 96, 255), width=size//20)
    
    # Save
    os.makedirs('static/icons', exist_ok=True)
    img.save(f'static/icons/icon-{size}x{size}.png')
    print(f"Generated icon-{size}x{size}.png")

# Generate all required sizes
sizes = [72, 96, 128, 144, 152, 192, 384, 512]
for size in sizes:
    generate_icon(size)

print("All icons generated successfully!")