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

# ── Design Tokens ────────────────────────────────────────────────
# Neutral dark palette — no purple, no gradients.
BG_PRIMARY   = "#181818"   # window background
BG_CARD      = "#222222"   # card / section surface
BG_INPUT     = "#2c2c2c"   # input fields
BORDER       = "#3a3a3a"   # subtle borders
TEXT_PRIMARY  = "#dcdcdc"   # main text
TEXT_SECONDARY = "#8a8a8a" # labels, hints
ACCENT       = "#3b82f6"   # blue — functional, not decorative
ACCENT_PRESS = "#2563eb"   # pressed state
GREEN        = "#22c55e"   # success
RED          = "#ef4444"   # error

# Type scale — two weights, three sizes.
FAMILY       = "Segoe UI"
TYPE_H1      = (FAMILY, 14, "bold")   # page title
TYPE_SECTION = (FAMILY, 11, "bold")   # section headers
TYPE_BODY    = (FAMILY, 10)           # labels, inputs, buttons
TYPE_CAPTION = (FAMILY, 9)            # hints

# Spacing & radii (kept to two values: 0 and 4).
PAD_SECTION  = 12
PAD_ROW      = 6
RADIUS       = 0   # tkinter doesn't support border-radius; keep flat


# ── Reusable widget factories ────────────────────────────────────
def _label(parent, text, font=TYPE_BODY, fg=TEXT_SECONDARY):
    return tk.Label(parent, text=text, font=font, fg=fg, bg=parent["bg"])


def _entry(parent, var, width=40):
    return tk.Entry(
        parent, textvariable=var, width=width,
        font=TYPE_BODY, fg=TEXT_PRIMARY, bg=BG_INPUT,
        insertbackground=TEXT_PRIMARY, relief="flat",
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT,
    )


def _dropdown(parent, var, options):
    om = tk.OptionMenu(parent, var, *options)
    om.config(
        font=TYPE_BODY, fg=TEXT_PRIMARY, bg=BG_INPUT,
        activebackground=BG_INPUT, activeforeground=TEXT_PRIMARY,
        relief="flat", highlightthickness=0, bd=0, indicatoron=True,
    )
    om["menu"].config(
        font=TYPE_BODY, fg=TEXT_PRIMARY, bg=BG_INPUT,
        activebackground=ACCENT, activeforeground="#fff",
    )
    return om


def _spinbox(parent, var, lo, hi, w=6):
    return tk.Spinbox(
        parent, textvariable=var, from_=lo, to=hi, width=w,
        font=TYPE_BODY, fg=TEXT_PRIMARY, bg=BG_INPUT,
        buttonbackground=BG_CARD, relief="flat",
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=ACCENT,
    )


def _button(parent, text, cmd, primary=False, w=12):
    bg = ACCENT if primary else BG_CARD
    pressed = ACCENT_PRESS if primary else BORDER
    btn = tk.Button(
        parent, text=text, command=cmd, width=w,
        font=TYPE_BODY, fg="#fff" if primary else TEXT_PRIMARY,
        bg=bg, activebackground=pressed, activeforeground="#fff",
        relief="flat", bd=0, cursor="hand2",
    )
    # Subtle state change — no glow, just a shade shift.
    btn.bind("<Enter>", lambda _: btn.config(bg=pressed))
    btn.bind("<Leave>", lambda _: btn.config(bg=bg))
    return btn


# ── Section wrapper ──────────────────────────────────────────────
def _section(parent, title):
    """Returns an inner frame you can pack rows into."""
    card = tk.Frame(parent, bg=BG_CARD, highlightthickness=1,
                    highlightbackground=BORDER)
    card.pack(fill="x", pady=(0, PAD_SECTION))

    tk.Label(card, text=title, font=TYPE_SECTION, fg=TEXT_PRIMARY,
             bg=BG_CARD, anchor="w").pack(fill="x", padx=PAD_SECTION,
                                          pady=(PAD_SECTION, 4))

    inner = tk.Frame(card, bg=BG_CARD)
    inner.pack(fill="x", padx=PAD_SECTION, pady=(0, PAD_SECTION))
    return inner


def _row(parent, label_text, widget, browse_cmd=None):
    """Label + widget on one row, optional browse button."""
    row = tk.Frame(parent, bg=BG_CARD)
    row.pack(fill="x", pady=PAD_ROW)

    _label(row, label_text, fg=TEXT_SECONDARY).pack(side="left", padx=(0, 8))
    widget.pack(side="left", fill="x", expand=True)

    if browse_cmd:
        _button(row, "Browse", browse_cmd, w=8).pack(side="left", padx=(6, 0))


# ═══════════════════════════════════════════════════════════════════
class QRCodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator")
        self.root.geometry("620x820")
        self.root.configure(bg=BG_PRIMARY)
        self.root.resizable(False, False)

        # Scrollable area
        canvas = tk.Canvas(root, bg=BG_PRIMARY, highlightthickness=0)
        sb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        wrapper = tk.Frame(canvas, bg=BG_PRIMARY)
        wrapper.bind("<Configure>",
                     lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=wrapper, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-int(e.delta / 120), "units"))

        body = tk.Frame(wrapper, bg=BG_PRIMARY)
        body.pack(fill="x", padx=20, pady=16)

        # ── Title ──
        tk.Label(body, text="QR Code Generator", font=TYPE_H1,
                 fg=TEXT_PRIMARY, bg=BG_PRIMARY).pack(anchor="w")
        tk.Label(body, text="Generate and customise QR codes.",
                 font=TYPE_CAPTION, fg=TEXT_SECONDARY,
                 bg=BG_PRIMARY).pack(anchor="w", pady=(2, 14))

        # ── Input ──
        sec = _section(body, "Input")

        self.url_var = tk.StringVar()
        _row(sec, "URL or text", _entry(sec, self.url_var))

        self.filename_var = tk.StringVar(value="my_qrcode")
        _row(sec, "Filename", _entry(sec, self.filename_var))

        self.dir_var = tk.StringVar(
            value=os.path.join(os.path.expanduser("~"), "Downloads"))
        _row(sec, "Save to", _entry(sec, self.dir_var, 30),
             browse_cmd=self._browse_dir)

        # ── Style ──
        sec2 = _section(body, "Style")

        self.fill_var = tk.StringVar(value="black")
        _row(sec2, "Fill colour",
             _dropdown(sec2, self.fill_var,
                       ["black", "red", "blue", "green", "orange",
                        "purple", "darkblue", "darkred", "white"]))

        self.bg_var = tk.StringVar(value="white")
        _row(sec2, "Background",
             _dropdown(sec2, self.bg_var,
                       ["white", "lightgray", "yellow", "lightblue",
                        "lightgreen", "pink", "black"]))

        self.shape_var = tk.StringVar(value="Square")
        _row(sec2, "Dot shape",
             _dropdown(sec2, self.shape_var,
                       ["Square", "Circle", "Rounded",
                        "Vertical Bars", "Horizontal Bars"]))

        self.gradient_var = tk.StringVar(value="Solid")
        _row(sec2, "Colour mode",
             _dropdown(sec2, self.gradient_var,
                       ["Solid", "Radial Gradient", "Square Gradient",
                        "Horizontal Gradient", "Vertical Gradient"]))

        # ── Options ──
        sec3 = _section(body, "Options")

        num_row = tk.Frame(sec3, bg=BG_CARD)
        num_row.pack(fill="x", pady=PAD_ROW)
        _label(num_row, "Box size").pack(side="left", padx=(0, 6))
        self.box_var = tk.IntVar(value=10)
        _spinbox(num_row, self.box_var, 1, 40).pack(side="left")
        _label(num_row, "Border").pack(side="left", padx=(20, 6))
        self.border_var = tk.IntVar(value=4)
        _spinbox(num_row, self.border_var, 1, 20).pack(side="left")

        self.logo_var = tk.StringVar()
        _row(sec3, "Centre logo", _entry(sec3, self.logo_var, 26),
             browse_cmd=self._browse_logo)

        # ── Action ──
        btn_area = tk.Frame(body, bg=BG_PRIMARY)
        btn_area.pack(fill="x", pady=(4, 10))
        self.gen_btn = _button(btn_area, "Generate", self._generate,
                               primary=True, w=20)
        self.gen_btn.pack()

        # ── Preview ──
        preview = tk.Frame(body, bg=BG_CARD, highlightthickness=1,
                           highlightbackground=BORDER)
        preview.pack(fill="x")

        _label(preview, "Preview", font=TYPE_SECTION,
               fg=TEXT_SECONDARY).pack(pady=(PAD_SECTION, 4))
        self.img_label = tk.Label(preview, bg=BG_CARD)
        self.img_label.pack(pady=(0, 4))

        self.status_var = tk.StringVar(value="No QR code generated yet.")
        self.status_label = tk.Label(preview, textvariable=self.status_var,
                                     font=TYPE_CAPTION, fg=TEXT_SECONDARY,
                                     bg=BG_CARD)
        self.status_label.pack(pady=(0, PAD_SECTION))

    # ── Callbacks ────────────────────────────────────────────────
    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.dir_var.set(d)

    def _browse_logo(self):
        f = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if f:
            self.logo_var.set(f)

    def _generate(self):
        url = self.url_var.get().strip()
        name = self.filename_var.get().strip()
        dest = self.dir_var.get().strip()

        if not url:
            messagebox.showerror("Missing input", "Enter a URL or text.")
            return
        if not name:
            messagebox.showerror("Missing input", "Enter a filename.")
            return

        # Show working state
        self.gen_btn.config(text="Generating...", state="disabled")
        self.root.update_idletasks()

        out = os.path.join(dest, f"{name}.png")
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
            "Radial Gradient":     RadialGradiantColorMask(
                back_color=bg_rgb, center_color=fill_rgb, edge_color=(0,0,0)),
            "Square Gradient":     SquareGradiantColorMask(
                back_color=bg_rgb, center_color=fill_rgb, edge_color=(0,0,0)),
            "Horizontal Gradient": HorizontalGradiantColorMask(
                back_color=bg_rgb, left_color=fill_rgb, right_color=(0,0,0)),
            "Vertical Gradient":   VerticalGradiantColorMask(
                back_color=bg_rgb, top_color=fill_rgb, bottom_color=(0,0,0)),
        }
        mask = masks.get(self.gradient_var.get(),
                         SolidFillColorMask(front_color=fill_rgb, back_color=bg_rgb))

        logo = self.logo_var.get().strip()

        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=self.box_var.get(),
                border=self.border_var.get(),
            )
            qr.add_data(url)

            kw = dict(image_factory=StyledPilImage,
                      module_drawer=drawer, color_mask=mask)
            if logo and os.path.exists(logo):
                kw["embeded_image_path"] = logo
            elif logo:
                messagebox.showwarning("File not found",
                                       f"Logo not found:\n{logo}")

            img = qr.make_image(**kw)
            img.save(out)

            # Success
            self.status_var.set(f"Saved to {out}")
            self.status_label.config(fg=GREEN)

            preview = Image.open(out)
            preview.thumbnail((200, 200), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview)
            self.img_label.config(image=photo)
            self.img_label.image = photo

        except Exception as exc:
            self.status_var.set(f"Error: {exc}")
            self.status_label.config(fg=RED)

        finally:
            # Restore button
            self.gen_btn.config(text="Generate", state="normal")


# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    QRCodeGeneratorApp(root)
    root.mainloop()
