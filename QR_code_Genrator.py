import qrcode
url=input("Enter the URL or text to generate QR Code: ").strip()
file_path="C:\\Users\\Levono\\Documents\\qr_code.png"

qr=qrcode.QRCode()
qr.add_data(url)

img=qr.make_image(fill_color="black", back_color="white")
img.save(file_path)

print("QR Code generated and saved to", file_path)
