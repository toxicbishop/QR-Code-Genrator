import qrcode
url=input("Enter the URL or text to generate QR Code: ").strip()
filename=input("Enter the filename (without extension): ").strip()
fill_col=input("Enter fill color (default black): ").strip()
back_col=input("Enter background color (default white): ").strip()

fill_col = fill_col if fill_col else "black"
back_col = back_col if back_col else "white"

file_path=f"C:\\Users\\Levono\\Downloads\\{filename}.png"

qr=qrcode.QRCode()
qr.add_data(url)

img=qr.make_image(fill_color=fill_col, back_color=back_col)
img.save(file_path)

print("QR Code generated and saved to", file_path)