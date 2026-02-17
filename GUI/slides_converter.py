import os
from pdf2image import convert_from_path
# Install Configuration
# # Install system dependency (poppler-utils)
# sudo apt-get update
# sudo apt-get install poppler-utils
#
# # Install Python package
# pip3 install pdf2image

pdf_path = "Pop-windows WIB.pdf"  # Your PDF file
output_dir = "output_pngs"
os.makedirs(output_dir, exist_ok=True)

# Convert PDF pages to images
pages = convert_from_path(pdf_path, dpi=200)  # dpi=200 for good quality

# Save each page as PNG named by page number
for i, page in enumerate(pages, start=1):
    page_path = os.path.join(output_dir, f"{i}.png")
    page.save(page_path, "PNG")

print(f"✅ Converted {len(pages)} pages to PNGs named 1.png, 2.png, ... in '{output_dir}'")