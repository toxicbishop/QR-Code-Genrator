import qrcode
from PIL import ImageColor, ImageTk, Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import (
    SquareModuleDrawer, CircleModuleDrawer, RoundedModuleDrawer,
    VerticalBarsDrawer, HorizontalBarsDrawer
)
from qrcode.image.styles.colormasks import (
    SolidFillColorMask, RadialGradiantColorMask, SquareGradiantColorMask,
    HorizontalGradiantColorMask, VerticalGradiantColorMask
)
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import os
import subprocess
import tempfile
import io

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CustomQRCodeGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Configuration")
        self.geometry("1100x750")
        self.minsize(900, 600)
        
        # Assets resolution for PyInstaller
        import sys
        if hasattr(sys, '_MEIPASS'):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.logos_dir = os.path.join(self.base_dir, "assets", "logos")
        self.logo_paths = {}
        
        # Grid config: 1 row, 2 columns
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=4) # Left panel width weight
        self.grid_columnconfigure(1, weight=5) # Right panel width weight
        
        # Set up variables early so trace can be bound
        self._init_vars()
        
        # --- Left Panel (Configuration) ---
        self.left_panel = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        header_lbl = ctk.CTkLabel(self.left_panel, text="Configuration", font=ctk.CTkFont(size=24, weight="bold"))
        header_lbl.pack(anchor="w", pady=(0, 15))
        
        self.setup_content_section()
        self.setup_appearance_section()
        self.setup_customization_section()
        self.setup_logo_section()

        # --- Right Panel (Live Preview) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        preview_lbl = ctk.CTkLabel(self.right_panel, text="Live Preview", font=ctk.CTkFont(size=14, weight="bold"))
        preview_lbl.pack(anchor="w", padx=5, pady=5)
        
        self.preview_frame = ctk.CTkFrame(self.right_panel, fg_color=("gray80", "gray12"), corner_radius=8)
        self.preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.preview_image_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.download_btn = ctk.CTkButton(self.right_panel, text="Download QR Code", font=ctk.CTkFont(size=14, weight="bold"), height=40, command=self.download_qr)
        self.download_btn.pack(fill="x", padx=5, pady=(20, 10))
        
        self.auto_open_cb = ctk.CTkCheckBox(self.right_panel, text="Auto-open after generation", variable=self.auto_open_var)
        self.auto_open_cb.pack(anchor="e", padx=5, pady=5)
        
        # Preview Job ID
        self._preview_job = None
        
        # Initial draw
        self.schedule_live_preview()
        
    def _init_vars(self):
        # Content
        self.url_var = tk.StringVar(value="https://example.com")
        self.filename_var = tk.StringVar(value="my_qrcode")
        self.dir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        
        # Appearance
        self.fill_var = tk.StringVar(value="black")
        self.bg_var = tk.StringVar(value="white")
        self.shape_var = tk.StringVar(value="Square")
        self.gradient_var = tk.StringVar(value="Solid")
        
        # Customization
        self.box_var = tk.DoubleVar(value=12) # Use double for ctk slider
        self.border_var = tk.DoubleVar(value=4)
        self.logo_scale_var = tk.DoubleVar(value=0.2)
        
        # Logo Options
        self.use_social_var = tk.BooleanVar(value=False)
        self.logo_menu_var = tk.StringVar(value="None")
        self.custom_logo_var = tk.StringVar(value="")
        self.remove_bg_var = tk.BooleanVar(value=False)
        
        self.auto_open_var = ctk.BooleanVar(value=False)
        
        # Bind traces for live preview
        vars_to_trace = [
            self.url_var, self.fill_var, self.bg_var, 
            self.shape_var, self.gradient_var, self.box_var, 
            self.border_var, self.logo_scale_var, self.use_social_var,
            self.logo_menu_var, self.custom_logo_var, self.remove_bg_var
        ]
        for v in vars_to_trace:
            v.trace_add("write", lambda *args: self.schedule_live_preview())

    def _create_section(self, title):
        frame = ctk.CTkFrame(self.left_panel, fg_color=("gray85", "gray14"), corner_radius=8)
        frame.pack(fill="x", pady=8)
        lbl = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        lbl.pack(anchor="w", padx=15, pady=(15, 5))
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(5, 15))
        return content

    def setup_content_section(self):
        sec = self._create_section("Content")
        
        ctk.CTkLabel(sec, text="URL or text", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(sec, textvariable=self.url_var).pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(sec, text="Filename", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        ctk.CTkEntry(sec, textvariable=self.filename_var).pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(sec, text="Save location", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        loc_row = ctk.CTkFrame(sec, fg_color="transparent")
        loc_row.pack(fill="x")
        ctk.CTkEntry(loc_row, textvariable=self.dir_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(loc_row, text="Browse", width=80, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self.browse_save_dir).pack(side="right")

    def setup_appearance_section(self):
        sec = self._create_section("Appearance")
        
        # Colors row
        col_row = ctk.CTkFrame(sec, fg_color="transparent")
        col_row.pack(fill="x", pady=(0, 10))
        
        # FG
        fg_frame = ctk.CTkFrame(col_row, fg_color="transparent")
        fg_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(fg_frame, text="Foreground", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        fg_inner = ctk.CTkFrame(fg_frame, fg_color="transparent")
        fg_inner.pack(fill="x")
        
        # Color preview/entry
        self.fg_preview = ctk.CTkEntry(fg_inner, textvariable=self.fill_var)
        self.fg_preview.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(fg_inner, text="Pick", width=50, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=lambda: self.pick_color(self.fill_var)).pack(side="right")
        
        # BG
        bg_frame = ctk.CTkFrame(col_row, fg_color="transparent")
        bg_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(bg_frame, text="Background", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        bg_inner = ctk.CTkFrame(bg_frame, fg_color="transparent")
        bg_inner.pack(fill="x")
        
        self.bg_preview = ctk.CTkEntry(bg_inner, textvariable=self.bg_var)
        self.bg_preview.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(bg_inner, text="Pick", width=50, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=lambda: self.pick_color(self.bg_var)).pack(side="right")
        
        # Shapes & Modes row
        shape_row = ctk.CTkFrame(sec, fg_color="transparent")
        shape_row.pack(fill="x")
        
        sh_frame = ctk.CTkFrame(shape_row, fg_color="transparent")
        sh_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(sh_frame, text="Dot shape", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        opts = ["Square", "Circle", "Rounded", "Vertical Bars", "Horizontal Bars"]
        ctk.CTkOptionMenu(sh_frame, variable=self.shape_var, values=opts).pack(fill="x")
        
        cm_frame = ctk.CTkFrame(shape_row, fg_color="transparent")
        cm_frame.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(cm_frame, text="Color mode", text_color="gray60", font=ctk.CTkFont(size=12)).pack(anchor="w")
        gopts = ["Solid", "Radial Gradient", "Square Gradient", "Horizontal Gradient", "Vertical Gradient"]
        ctk.CTkOptionMenu(cm_frame, variable=self.gradient_var, values=gopts).pack(fill="x")

    def setup_customization_section(self):
        sec = self._create_section("QR Customization")
        
        # Row 1: Box Size & Border Thickness
        r1 = ctk.CTkFrame(sec, fg_color="transparent")
        r1.pack(fill="x", pady=5)
        
        # Box size
        f1 = ctk.CTkFrame(r1, fg_color="transparent")
        f1.pack(side="left", fill="x", expand=True, padx=(0, 10))
        h1 = ctk.CTkFrame(f1, fg_color="transparent")
        h1.pack(fill="x")
        ctk.CTkLabel(h1, text="Box size", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        self.box_val_lbl = ctk.CTkLabel(h1, text="12", font=ctk.CTkFont(size=12))
        self.box_val_lbl.pack(side="right")
        ctk.CTkSlider(f1, from_=1, to=40, variable=self.box_var, command=lambda v: self.box_val_lbl.configure(text=f"{int(v)}")).pack(fill="x")
        self.box_val_lbl.configure(text=f"{int(self.box_var.get())}")
        
        # Border
        f2 = ctk.CTkFrame(r1, fg_color="transparent")
        f2.pack(side="left", fill="x", expand=True)
        h2 = ctk.CTkFrame(f2, fg_color="transparent")
        h2.pack(fill="x")
        ctk.CTkLabel(h2, text="Border thickness", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        self.border_val_lbl = ctk.CTkLabel(h2, text="4", font=ctk.CTkFont(size=12))
        self.border_val_lbl.pack(side="right")
        ctk.CTkSlider(f2, from_=1, to=20, variable=self.border_var, command=lambda v: self.border_val_lbl.configure(text=f"{int(v)}")).pack(fill="x")
        self.border_val_lbl.configure(text=f"{int(self.border_var.get())}")
        
    def setup_logo_section(self):
        sec = self._create_section("Logo Options")
        
        self.refresh_logos()
        logo_options = ["None"] + list(self.logo_paths.keys())
        
        row1 = ctk.CTkFrame(sec, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row1, text="Pick a social media icon", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        self.logo_om = ctk.CTkOptionMenu(row1, variable=self.logo_menu_var, values=logo_options)
        self.logo_om.pack(side="right", fill="x", expand=True, padx=(20, 0))
        
        row2 = ctk.CTkFrame(sec, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row2, text="Custom logo file", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        
        row2_inner = ctk.CTkFrame(row2, fg_color="transparent")
        row2_inner.pack(side="right", fill="x", expand=True, padx=(20, 0))
        ctk.CTkEntry(row2_inner, textvariable=self.custom_logo_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkButton(row2_inner, text="Browse", width=80, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self.browse_custom_logo).pack(side="right")
        
        row3 = ctk.CTkFrame(sec, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(row3, text="Intelligently strip logo background", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        ctk.CTkSwitch(row3, text="", variable=self.remove_bg_var, onvalue=True, offvalue=False).pack(side="right")
        
        row4 = ctk.CTkFrame(sec, fg_color="transparent")
        row4.pack(fill="x")
        h4 = ctk.CTkFrame(row4, fg_color="transparent")
        h4.pack(fill="x")
        ctk.CTkLabel(h4, text="Logo scale", text_color="gray60", font=ctk.CTkFont(size=12)).pack(side="left")
        self.scale_val_lbl = ctk.CTkLabel(h4, text="0.20", font=ctk.CTkFont(size=12))
        self.scale_val_lbl.pack(side="right")
        ctk.CTkSlider(row4, from_=0.05, to=0.5, variable=self.logo_scale_var, command=lambda v: self.scale_val_lbl.configure(text=f"{v:.2f}")).pack(fill="x")
        self.scale_val_lbl.configure(text=f"{self.logo_scale_var.get():.2f}")

    # --- Actions & Logic ---
    def pick_color(self, var):
        color = colorchooser.askcolor(title="Choose Colour")[1]
        if color:
            var.set(color)

    def browse_save_dir(self):
        d = filedialog.askdirectory()
        if d: self.dir_var.set(d)
        
    def browse_custom_logo(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if f: self.custom_logo_var.set(f)

    def refresh_logos(self):
        self.logo_paths = {}
        if os.path.exists(self.logos_dir):
            for f in sorted(os.listdir(self.logos_dir)):
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
                    name = os.path.splitext(f)[0]
                    self.logo_paths[name] = os.path.join(self.logos_dir, f)

    def schedule_live_preview(self):
        if self._preview_job:
            self.after_cancel(self._preview_job)
        # Debounce for 350ms
        self._preview_job = self.after(350, self.generate_qr_core)

    def generate_qr_core(self, save_path=None):
        url = self.url_var.get().strip()
        if not url:
            # Clear preview if empty
            self.preview_image_label.configure(image="")
            return

        # Setup Colors
        fill = self.fill_var.get().strip() or "black"
        bg   = self.bg_var.get().strip() or "white"
        try:
            fill_rgb = ImageColor.getrgb(fill)
            bg_rgb   = ImageColor.getrgb(bg)
        except ValueError:
            fill_rgb, bg_rgb = (0, 0, 0), (255, 255, 255)

        drawers = {
            "Circle":          CircleModuleDrawer(),
            "Rounded":         RoundedModuleDrawer(),
            "Vertical Bars":   VerticalBarsDrawer(),
            "Horizontal Bars": HorizontalBarsDrawer(),
        }
        drawer = drawers.get(self.shape_var.get(), SquareModuleDrawer())

        masks = {
            "Radial Gradient":     RadialGradiantColorMask(back_color=bg_rgb, center_color=fill_rgb, edge_color=(0,0,0)),
            "Square Gradient":     SquareGradiantColorMask(back_color=bg_rgb, center_color=fill_rgb, edge_color=(0,0,0)),
            "Horizontal Gradient": HorizontalGradiantColorMask(back_color=bg_rgb, left_color=fill_rgb, right_color=(0,0,0)),
            "Vertical Gradient":   VerticalGradiantColorMask(back_color=bg_rgb, top_color=fill_rgb, bottom_color=(0,0,0)),
        }
        mask = masks.get(self.gradient_var.get(), SolidFillColorMask(front_color=fill_rgb, back_color=bg_rgb))

        logo = None
        choice = self.logo_menu_var.get()
        if choice != "None" and choice in self.logo_paths:
            logo = self.logo_paths[choice]
            
        custom = self.custom_logo_var.get().strip()
        if custom: # Custom takes precedence
            logo = custom
            
        temp_logo = None

        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=int(self.box_var.get()),
                border=int(self.border_var.get()),
            )
            qr.add_data(url)

            kw = dict(image_factory=StyledPilImage, module_drawer=drawer, color_mask=mask)
            
            if logo and os.path.exists(logo):
                img_to_process = None
                if self.remove_bg_var.get():
                    if not REMBG_AVAILABLE:
                        img_to_process = Image.open(logo)
                    else:
                        try:
                            with open(logo, "rb") as f:
                                input_data = f.read()
                            output_data = remove(input_data)
                            img_to_process = Image.open(io.BytesIO(output_data))
                        except Exception:
                            img_to_process = Image.open(logo)
                else:
                    img_to_process = Image.open(logo)
                        
                if img_to_process:
                    img_to_process = img_to_process.convert("RGBA")
                    bbox = img_to_process.getbbox()
                    if bbox:
                        img_to_process = img_to_process.crop(bbox)
                    
                    w, h = img_to_process.size
                    size = max(w, h)
                    
                    current_scale = self.logo_scale_var.get()
                    canvas_size = int(size * (0.3 / current_scale))
                    if canvas_size <= size: canvas_size = size
                    
                    final_logo = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
                    final_logo.paste(img_to_process, ((canvas_size - w) // 2, (canvas_size - h) // 2))
                    
                    fd, temp_path = tempfile.mkstemp(suffix=".png")
                    with os.fdopen(fd, "wb") as f:
                        final_logo.save(f, format="PNG")
                    temp_logo = temp_path
                    kw["embeded_image_path"] = temp_logo

            # Generate image
            img = qr.make_image(**kw)
            
            # If a save path was provided (Download button clicked), save it
            if save_path:
                img.save(save_path)
                # Cleanup temp logo early here if saving
                if temp_logo and os.path.exists(temp_logo):
                    try:
                        os.remove(temp_logo)
                    except Exception:
                        pass
                return save_path

            # Otherwise, update Live Preview
            # Maintain a reasonable size to preview cleanly
            pil_img = img.get_image() # For StyledPilImage this returns PIL primitive sometimes or it IS the PIL primitive
            if not isinstance(pil_img, Image.Image):
                # styledpilimage itself is an object containing the core image
                pil_img = img._img
                
            # Resize for preview
            max_size = 400
            pil_img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(pil_img.width, pil_img.height))
            self.preview_image_label.configure(image=ctk_img)
            self.preview_image_label.image = ctk_img # Keep ref

        except Exception as e:
            print(f"Error during generation: {e}")
        finally:
            if not save_path and temp_logo and os.path.exists(temp_logo):
                try:
                    os.remove(temp_logo)
                except Exception:
                    pass

    def download_qr(self):
        dest = self.dir_var.get().strip()
        name = self.filename_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please provide a valid filename.")
            return
            
        if not os.path.exists(dest):
            try:
                os.makedirs(dest)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to access save directory:\n{e}")
                return
                
        out_path = os.path.join(dest, f"{name}.png")
        self.download_btn.configure(text="Generating...", state="disabled")
        self.update_idletasks()
        
        saved_path = self.generate_qr_core(save_path=out_path)
        
        self.download_btn.configure(text="Download QR Code", state="normal")
        
        if saved_path:
            messagebox.showinfo("Success", f"Saved successfully to:\n{saved_path}")
            if self.auto_open_var.get():
                if os.name == 'nt':
                    os.startfile(saved_path)
                else:
                    subprocess.run(['open' if os.name == 'posix' else 'xdg-open', saved_path])


if __name__ == "__main__":
    app = CustomQRCodeGeneratorApp()
    app.mainloop()
