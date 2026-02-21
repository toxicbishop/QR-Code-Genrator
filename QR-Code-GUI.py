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
from tkinter import filedialog, messagebox
import os

# ── Dark Mode Color Palette ──────────────────────────────────────
BG           = "#1e1e2e"
SURFACE      = "#2a2a3d"
INPUT_BG     = "#33334d"
ACCENT       = "#7c3aed"
ACCENT_HOVER = "#9f67ff"
TEXT         = "#e0e0e0"
TEXT_DIM     = "#a0a0b0"
SUCCESS      = "#4ade80"
ERROR        = "#f87171"
BORDER_CLR   = "#3d3d5c"

FONT         = ("Segoe UI", 10)
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_HEADER  = ("Segoe UI", 18, "bold")
FONT_SUB     = ("Segoe UI", 10)

# ── Helper: styled widgets ───────────────────────────────────────
def make_label(parent, text, font=FONT, fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=parent["bg"], **kw)

def make_entry(parent, var, width=42):
    e = tk.Entry(parent, textvariable=var, width=width,
                 font=FONT, fg=TEXT, bg=INPUT_BG,
                 insertbackground=TEXT, relief="flat",
                 highlightthickness=1, highlightcolor=ACCENT,
                 highlightbackground=BORDER_CLR)
    return e

def make_option(parent, var, values):
    om = tk.OptionMenu(parent, var, *values)
    om.config(font=FONT, fg=TEXT, bg=INPUT_BG, activebackground=ACCENT,
              activeforeground="white", relief="flat", highlightthickness=0,
              indicatoron=True, bd=0)
    om["menu"].config(font=FONT, fg=TEXT, bg=INPUT_BG,
                      activebackground=ACCENT, activeforeground="white")
    return om

def make_spinbox(parent, var, from_, to_, width=6):
    sb = tk.Spinbox(parent, textvariable=var, from_=from_, to=to_, width=width,
                    font=FONT, fg=TEXT, bg=INPUT_BG,
                    buttonbackground=SURFACE, relief="flat",
                    highlightthickness=1, highlightcolor=ACCENT,
                    highlightbackground=BORDER_CLR)
    return sb

def make_button(parent, text, command, accent=False, width=10):
    bg_c = ACCENT if accent else SURFACE
    hover = ACCENT_HOVER if accent else BORDER_CLR
    b = tk.Button(parent, text=text, command=command,
                  font=FONT_BOLD if accent else FONT, width=width,
                  fg="white", bg=bg_c, activebackground=hover,
                  activeforeground="white", relief="flat", cursor="hand2", bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=hover))
    b.bind("<Leave>", lambda e: b.config(bg=bg_c))
    return b


# ── Section card ─────────────────────────────────────────────────
def make_section(parent, title):
    frame = tk.Frame(parent, bg=SURFACE, bd=0, highlightthickness=1,
                     highlightbackground=BORDER_CLR)
    frame.pack(fill="x", pady=(0, 12))
    header = tk.Label(frame, text=title, font=FONT_BOLD, fg=ACCENT,
                      bg=SURFACE, anchor="w")
    header.pack(fill="x", padx=14, pady=(10, 4))
    inner = tk.Frame(frame, bg=SURFACE)
    inner.pack(fill="x", padx=14, pady=(0, 10))
    return inner


# ── Row helper ───────────────────────────────────────────────────
def add_row(section, label_text, widget, browse_cmd=None):
    row = tk.Frame(section, bg=SURFACE)
    row.pack(fill="x", pady=3)
    lbl = tk.Label(row, text=label_text, font=FONT, fg=TEXT_DIM,
                   bg=SURFACE, width=20, anchor="w")
    lbl.pack(side="left")
    widget.pack(side="left", fill="x", expand=True)
    if browse_cmd:
        b = make_button(row, "Browse", browse_cmd, width=8)
        b.pack(side="left", padx=(6, 0))


# ═══════════════════════════════════════════════════════════════════
class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("650x860")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # ── Scrollable canvas ──
        canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg=BG)
        self.scroll_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Enable mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        container = tk.Frame(self.scroll_frame, bg=BG)
        container.pack(fill="x", padx=24, pady=16)

        # ── Header ──
        hdr = tk.Frame(container, bg=BG)
        hdr.pack(fill="x", pady=(0, 16))
        tk.Label(hdr, text="🔳  QR Code Generator", font=FONT_HEADER,
                 fg=TEXT, bg=BG).pack(anchor="w")
        tk.Label(hdr, text="Generate beautiful, customizable QR codes in seconds.",
                 font=FONT_SUB, fg=TEXT_DIM, bg=BG).pack(anchor="w", pady=(2, 0))

        # ── Section: Basic Info ──
        sec = make_section(container, "📋  Basic Info")
        self.url_var = tk.StringVar()
        add_row(sec, "URL / Text", make_entry(sec, self.url_var))

        self.filename_var = tk.StringVar(value="my_qrcode")
        add_row(sec, "Filename", make_entry(sec, self.filename_var))

        self.dir_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads"))
        add_row(sec, "Save to", make_entry(sec, self.dir_var, width=30),
                browse_cmd=self.browse_dir)

        # ── Section: Appearance ──
        sec2 = make_section(container, "🎨  Appearance")

        self.fill_col_var = tk.StringVar(value="black")
        fill_colors = ["black", "red", "blue", "green", "purple",
                       "orange", "darkblue", "darkred", "white"]
        add_row(sec2, "Fill Color", make_option(sec2, self.fill_col_var, fill_colors))

        self.back_col_var = tk.StringVar(value="white")
        back_colors = ["white", "lightgray", "yellow", "lightblue",
                       "lightgreen", "pink", "black"]
        add_row(sec2, "Background Color", make_option(sec2, self.back_col_var, back_colors))

        self.shape_var = tk.StringVar(value="Square")
        shapes = ["Square", "Circle", "Rounded", "Vertical Bars", "Horizontal Bars"]
        add_row(sec2, "Dot Shape", make_option(sec2, self.shape_var, shapes))

        self.color_style_var = tk.StringVar(value="Solid Color")
        styles = ["Solid Color", "Radial Gradient", "Square Gradient",
                  "Horizontal Gradient", "Vertical Gradient"]
        add_row(sec2, "Color Style", make_option(sec2, self.color_style_var, styles))

        # ── Section: Advanced ──
        sec3 = make_section(container, "⚙️  Advanced")

        size_row = tk.Frame(sec3, bg=SURFACE)
        size_row.pack(fill="x", pady=3)
        tk.Label(size_row, text="Box Size", font=FONT, fg=TEXT_DIM,
                 bg=SURFACE, width=20, anchor="w").pack(side="left")
        self.box_size_var = tk.IntVar(value=10)
        make_spinbox(size_row, self.box_size_var, 1, 40).pack(side="left")

        tk.Label(size_row, text="     Border", font=FONT, fg=TEXT_DIM,
                 bg=SURFACE).pack(side="left", padx=(10, 0))
        self.border_var = tk.IntVar(value=4)
        make_spinbox(size_row, self.border_var, 1, 20).pack(side="left", padx=(6, 0))

        self.logo_var = tk.StringVar()
        add_row(sec3, "Center Logo", make_entry(sec3, self.logo_var, width=26),
                browse_cmd=self.browse_logo)

        # ── Generate Button ──
        btn_frame = tk.Frame(container, bg=BG)
        btn_frame.pack(fill="x", pady=(4, 8))
        gen_btn = make_button(btn_frame, "✨  Generate QR Code",
                              self.generate_qr, accent=True, width=28)
        gen_btn.pack(pady=4)

        # ── Preview area ──
        preview_card = tk.Frame(container, bg=SURFACE, bd=0,
                                highlightthickness=1,
                                highlightbackground=BORDER_CLR)
        preview_card.pack(fill="x", pady=(0, 8))

        tk.Label(preview_card, text="Preview", font=FONT_BOLD,
                 fg=TEXT_DIM, bg=SURFACE).pack(pady=(10, 4))

        self.img_label = tk.Label(preview_card, bg=SURFACE)
        self.img_label.pack(pady=(0, 6))

        self.result_var = tk.StringVar(value="Generate a QR code to see a preview here.")
        self.result_label = tk.Label(preview_card, textvariable=self.result_var,
                                     font=FONT, fg=TEXT_DIM, bg=SURFACE)
        self.result_label.pack(pady=(0, 12))

    # ── Browse callbacks ──
    def browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.dir_var.set(d)

    def browse_logo(self):
        f = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if f:
            self.logo_var.set(f)

    # ── Generate logic (unchanged from before) ──
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

        try:
            fill_rgb = ImageColor.getrgb(fill_col)
            back_rgb = ImageColor.getrgb(back_col)
        except ValueError:
            messagebox.showwarning("Warning",
                                   "Invalid color. Using black & white.")
            fill_rgb, back_rgb = (0, 0, 0), (255, 255, 255)

        # Shape
        shape = self.shape_var.get()
        drawers = {
            "Circle": CircleModuleDrawer(),
            "Rounded": RoundedModuleDrawer(),
            "Vertical Bars": VerticalBarsDrawer(),
            "Horizontal Bars": HorizontalBarsDrawer(),
        }
        module_drawer = drawers.get(shape, SquareModuleDrawer())

        # Color style
        style = self.color_style_var.get()
        masks = {
            "Radial Gradient": RadialGradiantColorMask(
                back_color=back_rgb, center_color=fill_rgb, edge_color=(0, 0, 0)),
            "Square Gradient": SquareGradiantColorMask(
                back_color=back_rgb, center_color=fill_rgb, edge_color=(0, 0, 0)),
            "Horizontal Gradient": HorizontalGradiantColorMask(
                back_color=back_rgb, left_color=fill_rgb, right_color=(0, 0, 0)),
            "Vertical Gradient": VerticalGradiantColorMask(
                back_color=back_rgb, top_color=fill_rgb, bottom_color=(0, 0, 0)),
        }
        color_mask = masks.get(
            style, SolidFillColorMask(front_color=fill_rgb, back_color=back_rgb))

        box_size = self.box_size_var.get()
        border = self.border_var.get()
        logo_path = self.logo_var.get().strip()

        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=box_size, border=border)
            qr.add_data(url)

            if logo_path and os.path.exists(logo_path):
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask,
                    embeded_image_path=logo_path)
            else:
                if logo_path:
                    messagebox.showwarning("Warning",
                                           f"Logo not found: {logo_path}")
                img = qr.make_image(
                    image_factory=StyledPilImage,
                    module_drawer=module_drawer,
                    color_mask=color_mask)

            img.save(file_path)

            # Update result
            self.result_var.set(f"✅  Saved to: {file_path}")
            self.result_label.config(fg=SUCCESS)

            # Show preview
            preview = Image.open(file_path)
            preview.thumbnail((220, 220), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview)
            self.img_label.config(image=photo)
            self.img_label.image = photo

        except Exception as e:
            self.result_var.set(f"❌  Error: {e}")
            self.result_label.config(fg=ERROR)


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()
