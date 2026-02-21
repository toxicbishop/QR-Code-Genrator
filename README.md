# 🔳 QR Code Generator

> A lightweight Python script that instantly converts any URL or text into a scannable QR code image.

---

## ✨ Features

- 📋 Accepts any URL or text as input
- 💾 Lets you name your QR code file
- 🎨 Customize QR code colors (fill and background)
- 📐 Adjust the box size and border thickness
- 🟢 Pick cool shapes for your QR code dots (circles, rounded, bars)
- 🖼️ Saves output as a `.png` image
- ⚡ Fast and simple — runs entirely in the terminal

---

## 🖼️ Example **Output**

![Generated QR Code](QR-Code.png)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/toxicbishop/QR-Code-Genrator.git
cd QR-Code-Genrator
```

### 2. Set up the virtual environment

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the script

```bash
python QR_code_Genrator.py
```

---

## 🛠️ Usage

When you run the script, you will be prompted to enter the URL, filename, color preferences, size, border, and shape:

```
Enter the URL or text to generate QR Code: https://example.com
Enter the filename (without extension): my_qrcode
Enter fill color (default black): blue
Enter background color (default white): yellow
Enter box size (1-20, default 10): 15
Enter border thickness (default 4): 5

Choose QR Code shape:
1. Square (default)
2. Circle
3. Rounded
4. Vertical Bars
5. Horizontal Bars
Enter choice (1-5): 3
```

Your QR code will be saved to:
```
C:\Users\Levono\Downloads\my_qrcode.png
```

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `qrcode` | QR code generation |
| `Pillow` | Image rendering |

> All dependencies are listed in `requirements.txt`

---

## 📄 License

This project is open source and free to use.
