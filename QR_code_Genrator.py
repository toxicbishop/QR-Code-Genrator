import qrcode
from PIL import ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import SolidFillColorMask

url = input("Enter the URL or text to generate QR Code: ").strip()
filename = input("Enter the filename (without extension): ").strip()
fill_col = input("Enter fill color (default black): ").strip()
back_col = input("Enter background color (default white): ").strip()

box_size_input = input("Enter box size (1-20, default 10): ").strip()
border_input = input("Enter border thickness (default 4): ").strip()

print("\nChoose QR Code shape:")
print("1. Square (default)")
print("2. Circle")
print("3. Rounded")
print("4. Vertical Bars")
print("5. Horizontal Bars")
shape_choice = input("Enter choice (1-5): ").strip()

fill_col = fill_col if fill_col else "black"
back_col = back_col if back_col else "white"
box_size = int(box_size_input) if box_size_input.isdigit() else 10
border = int(border_input) if border_input.isdigit() else 4

# Parse colors into RGB tuples required by SolidFillColorMask
try:
    fill_rgb = ImageColor.getrgb(fill_col)
    back_rgb = ImageColor.getrgb(back_col)
except ValueError:
    print("Invalid color name, falling back to black and white.")
    fill_rgb = (0, 0, 0)
    back_rgb = (255, 255, 255)

# Map shape choice to the correct drawer
if shape_choice == '2':
    module_drawer = CircleModuleDrawer()
elif shape_choice == '3':
    module_drawer = RoundedModuleDrawer()
elif shape_choice == '4':
    module_drawer = VerticalBarsDrawer()
elif shape_choice == '5':
    module_drawer = HorizontalBarsDrawer()
else:
    module_drawer = SquareModuleDrawer()

file_path = f"C:\\Users\\Levono\\Downloads\\{filename}.png"

qr = qrcode.QRCode(box_size=box_size, border=border)
qr.add_data(url)

img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=module_drawer,
    color_mask=SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb)
)
img.save(file_path)

print("QR Code generated and saved to", file_path)