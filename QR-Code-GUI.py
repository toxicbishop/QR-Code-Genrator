import qrcode
from PIL import ImageColor, ImageTk, Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask,
    RadialGradiantColorMask,
    SquareGradiantColorMask,
    HorizontalGradiantColorMask,
    VerticalGradiantColorMask
)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator GUI")
        self.root.geometry("600x700")
        
        # main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL
        ttk.Label(main_frame, text="URL / Text:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Filename
        ttk.Label(main_frame, text="Filename (without extension):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.filename_var = tk.StringVar(value="my_qrcode")
        ttk.Entry(main_frame, textvariable=self.filename_var, width=50).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Output Directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.dir_var = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Downloads'))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=38).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", width=10, command=self.browse_dir).pack(side=tk.LEFT)

        # Fill Color
        ttk.Label(main_frame, text="Fill Color:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fill_col_var = tk.StringVar(value="black")
        self.fill_col_combo = ttk.Combobox(main_frame, textvariable=self.fill_col_var, values=["black", "red", "blue", "green", "purple", "orange", "darkblue", "darkred"])
        self.fill_col_combo.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Background Color
        ttk.Label(main_frame, text="Background Color:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.back_col_var = tk.StringVar(value="white")
        self.back_col_combo = ttk.Combobox(main_frame, textvariable=self.back_col_var, values=["white", "lightgray", "yellow", "lightblue", "lightgreen", "pink"])
        self.back_col_combo.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Box Size and Border
        size_border_frame = ttk.Frame(main_frame)
        size_border_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(size_border_frame, text="Box Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.box_size_var = tk.IntVar(value=10)
        ttk.Spinbox(size_border_frame, from_=1, to=40, textvariable=self.box_size_var, width=5).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(size_border_frame, text="Border:").pack(side=tk.LEFT, padx=(0, 5))
        self.border_var = tk.IntVar(value=4)
        ttk.Spinbox(size_border_frame, from_=1, to=20, textvariable=self.border_var, width=5).pack(side=tk.LEFT)

        # Shape
        ttk.Label(main_frame, text="Shape:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.shape_var = tk.StringVar(value="Square")
        self.shape_combo = ttk.Combobox(main_frame, textvariable=self.shape_var, values=["Square", "Circle", "Rounded", "Vertical Bars", "Horizontal Bars"])
        self.shape_combo.grid(row=6, column=1, sticky=tk.W, pady=5)

        # Color Style
        ttk.Label(main_frame, text="Color Style:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.color_style_var = tk.StringVar(value="Solid Color")
        self.color_style_combo = ttk.Combobox(main_frame, textvariable=self.color_style_var, values=["Solid Color", "Radial Gradient", "Square Gradient", "Horizontal Gradient", "Vertical Gradient"])
        self.color_style_combo.grid(row=7, column=1, sticky=tk.W, pady=5)

        # Logo Path
        ttk.Label(main_frame, text="Center Logo (Optional):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.logo_var = tk.StringVar()
        logo_frame = ttk.Frame(main_frame)
        logo_frame.grid(row=8, column=1, sticky=tk.W, pady=5)
        ttk.Entry(logo_frame, textvariable=self.logo_var, width=38).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(logo_frame, text="Browse", width=10, command=self.browse_logo).pack(side=tk.LEFT)

        # Generate Button
        ttk.Button(main_frame, text="Generate QR Code", command=self.generate_qr).grid(row=9, column=0, columnspan=2, pady=20)
        
        # Image Display Label
        self.img_label = ttk.Label(main_frame)
        self.img_label.grid(row=10, column=0, columnspan=2, pady=10)
        
        # Result text
        self.result_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.result_var, foreground="green").grid(row=11, column=0, columnspan=2, pady=5)

    def browse_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dir_var.set(dir_path)

    def browse_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            self.logo_var.set(file_path)

    def generate_qr(self):
        url = self.url_var.get().strip()
        filename = self.filename_var.get().strip()
        directory = self.dir_var.get().strip()
        
        if not url:
            messagebox.showerror("Error", "URL/Text cannot be empty!")
            return
        if not filename:
            messagebox.showerror("Error", "Filename cannot be empty!")
            return
            
        file_path = os.path.join(directory, f"{filename}.png")
        
        fill_col = self.fill_col_var.get().strip() or "black"
        back_col = self.back_col_var.get().strip() or "white"
        
        # Parse colors
        try:
            fill_rgb = ImageColor.getrgb(fill_col)
            back_rgb = ImageColor.getrgb(back_col)
        except ValueError:
            messagebox.showwarning("Warning", "Invalid color name. Using black and white instead.")
            fill_rgb = (0, 0, 0)
            back_rgb = (255, 255, 255)

        # Shape
        shape_choice = self.shape_var.get()
        if shape_choice == "Circle":
            module_drawer = CircleModuleDrawer()
        elif shape_choice == "Rounded":
            module_drawer = RoundedModuleDrawer()
        elif shape_choice == "Vertical Bars":
            module_drawer = VerticalBarsDrawer()
        elif shape_choice == "Horizontal Bars":
            module_drawer = HorizontalBarsDrawer()
        else:
            module_drawer = SquareModuleDrawer()
            
        # Color Style
        color_style = self.color_style_var.get()
        if color_style == "Radial Gradient":
            color_mask = RadialGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=(0,0,0))
        elif color_style == "Square Gradient":
            color_mask = SquareGradiantColorMask(back_color=back_rgb, center_color=fill_rgb, edge_color=(0,0,0))
        elif color_style == "Horizontal Gradient":
            color_mask = HorizontalGradiantColorMask(back_color=back_rgb, left_color=fill_rgb, right_color=(0,0,0))
        elif color_style == "Vertical Gradient":
            color_mask = VerticalGradiantColorMask(back_color=back_rgb, top_color=fill_rgb, bottom_color=(0,0,0))
        else:
            color_mask = SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb)

        box_size = self.box_size_var.get()
        border = self.border_var.get()
        logo_path = self.logo_var.get().strip()
        
        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size, 
                border=border
            )
            qr.add_data(url)
            
            if logo_path and os.path.exists(logo_path):
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask,
                    embeded_image_path=logo_path
                )
            else:
                if logo_path:
                    messagebox.showwarning("Warning", f"Logo file not found: {logo_path}")
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask
                )
                
            img.save(file_path)
            self.result_var.set(f"Success! Saved to:\n{file_path}")
            
            # Show preview
            max_size = (200, 200)
            preview_img = Image.open(file_path)
            preview_img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)
            self.img_label.config(image=photo)
            self.img_label.image = photo
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()
