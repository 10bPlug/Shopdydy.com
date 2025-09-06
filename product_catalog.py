import os
from pathlib import Path
from datetime import datetime
from io import BytesIO

from PIL import Image
import xlsxwriter

# --- CONFIG ---
# Default to the current script directory so it works with the current folder
base_dir = Path(__file__).resolve().parent
image_folder = base_dir / "product"  # Scan images in the product folder
output_excel = base_dir / "product_catalog.xlsx"  # Save output in the current folder
usd_rate = 0.08  # Example: 1 GHS = 0.08 USD
supported_exts = {".png", ".jpg", ".jpeg"}  # Support more image types if needed

# --- FUNCTIONS ---
def extract_brand(product_name: str) -> str:
    words = product_name.split()
    return words[0] if words else "Unknown"

def guess_category(product_name: str):
    name = product_name.lower()
    if "laptop" in name or "macbook" in name:
        return "Laptop", ("Professional" if "pro" in name else "Business")
    elif "iphone" in name or "samsung" in name:
        return "Smartphone", "Flagship"
    elif "pen drive" in name or "flash" in name or "usb" in name:
        return "Storage", "USB Drive"
    elif "watch" in name:
        return "Wearables", "Smartwatch"
    else:
        return "Electronics", "Other"

def generate_description(product_name: str) -> str:
    return (
        f"The {product_name} is a premium tech product, offering excellent performance "
        f"and reliability. Designed for modern needs, it combines style and efficiency."
    )

def generate_features(product_name: str) -> str:
    return "• Durable build\n• High performance\n• Modern design\n• Warranty included"

def create_sku(category: str, index: int) -> str:
    # Use 4 digits to avoid collisions if >999 items
    return f"{category[:3].upper()}-{str(index).zfill(4)}"

# --- SAFETY CHECKS ---
if not image_folder.exists() or not image_folder.is_dir():
    raise FileNotFoundError(f"Image folder does not exist or is not a directory: {image_folder}")

output_excel.parent.mkdir(parents=True, exist_ok=True)

# --- PROCESS FILES ---
data = []
image_thumbnails = []

# Sort files for deterministic output
files = sorted(image_folder.iterdir(), key=lambda p: p.name.lower())

processed_count = 0
for file in files:
    if not file.is_file():
        continue
    if file.suffix.lower() not in supported_exts:
        continue

    product_name = file.stem
    brand = extract_brand(product_name)
    category, subcategory = guess_category(product_name)
    description = generate_description(product_name)
    features = generate_features(product_name)
    processed_count += 1
    sku = create_sku(category, processed_count)
    date_added = datetime.today().strftime('%Y-%m-%d')

    # Prices (placeholders)
    price_ghs = 1000
    price_usd = round(price_ghs * usd_rate, 2)

    data.append([
        product_name, category, subcategory, brand, description, features,
        "New", price_ghs, price_usd, "In Stock", str(file), sku, date_added
    ])

    # Create thumbnail safely
    try:
        with Image.open(file) as img:
            img.load()  # Ensure image is read before closing file handle
            img.thumbnail((80, 80))
            img_bytes = BytesIO()
            # Preserve format if possible, default to PNG
            fmt = "PNG"
            img.save(img_bytes, format=fmt)
            image_thumbnails.append(img_bytes.getvalue())
    except Exception as e:
        # Skip problematic image but keep processing others
        print(f"Warning: failed to process image {file}: {e}")
        # Add a placeholder (empty) for the thumbnail to keep alignment
        image_thumbnails.append(None)

# --- CREATE EXCEL ---
columns = [
    "Product Name", "Category", "Subcategory", "Brand", "Description", "Key Features",
    "Condition", "Price (GHS)", "Price (USD)", "Stock Status", "File Path", "SKU", "Date Added"
]

with xlsxwriter.Workbook(str(output_excel)) as workbook:
    worksheet = workbook.add_worksheet("Catalog")

    # Formats
    header_format = workbook.add_format({"bold": True, "bg_color": "#D9E1F2", "border": 1})
    wrap_top = workbook.add_format({"text_wrap": True, "valign": "top"})
    ghc_fmt = workbook.add_format({"num_format": '[$GHS] #,##0.00'})
    usd_fmt = workbook.add_format({"num_format": '$#,##0.00'})

    # Write headers
    for col_num, header in enumerate(["Thumbnail"] + columns):
        worksheet.write(0, col_num, header, header_format)

    # Freeze header row
    worksheet.freeze_panes(1, 0)

    # Write data with thumbnails
    for row_num, (row_data, img_data) in enumerate(zip(data, image_thumbnails), start=1):
        # Insert thumbnail if available
        if img_data:
            worksheet.insert_image(row_num, 0, "thumbnail.png", {
                "image_data": BytesIO(img_data),
                "x_scale": 1,
                "y_scale": 1,
                "x_offset": 2,
                "y_offset": 2
            })
        # Approximate row height to fit ~80px thumbnail
        worksheet.set_row(row_num, 80)

        # Write other columns
        for col_num, value in enumerate(row_data, start=1):
            # Apply wrapping to long text columns
            if col_num in (5, 6):  # Description, Key Features (1-based: 5,6; 0-based here +1)
                worksheet.write(row_num, col_num, value, wrap_top)
            elif col_num == 8:  # Price (GHS)
                worksheet.write_number(row_num, col_num, float(value), ghc_fmt)
            elif col_num == 9:  # Price (USD)
                worksheet.write_number(row_num, col_num, float(value), usd_fmt)
            else:
                worksheet.write(row_num, col_num, value)

    # Set column widths
    worksheet.set_column(0, 0, 12)  # Thumbnail
    worksheet.set_column(1, 1, 25)  # Product Name
    worksheet.set_column(2, 4, 18)  # Category, Subcategory, Brand
    worksheet.set_column(5, 6, 40)  # Description, Key Features
    worksheet.set_column(7, 9, 14)  # Condition, Price (GHS), Price (USD)
    worksheet.set_column(10, 10, 14)  # Stock Status
    worksheet.set_column(11, 11, 40)  # File Path
    worksheet.set_column(12, 13, 18)  # SKU, Date Added

print(f"Processed {processed_count} image(s) from {image_folder}")
print(f"Catalog saved to {output_excel}")