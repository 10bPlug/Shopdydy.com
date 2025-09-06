#!/usr/bin/env python3
"""
Enhanced Product Catalog Generator for Shopdydy.com
Creates a comprehensive product database with better categorization and multiple output formats.
"""

import os
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from io import BytesIO
import re

from PIL import Image
import xlsxwriter

# Configuration
BASE_DIR = Path(__file__).resolve().parent
IMAGE_FOLDER = BASE_DIR / "product"
OUTPUT_EXCEL = BASE_DIR / "product_catalog.xlsx"
OUTPUT_DB = BASE_DIR / "products.db"
OUTPUT_JSON = BASE_DIR / "products.json"
USD_RATE = 0.08  # 1 GHS = 0.08 USD
SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp"}

# Enhanced product categorization
CATEGORY_MAPPING = {
    # Computing & Laptops
    'laptop': ('Computing', 'Laptops', 15000, 30000),
    'dell': ('Computing', 'Laptops', 12000, 25000),
    'hp': ('Computing', 'Laptops', 10000, 20000),
    'acer': ('Computing', 'Laptops', 8000, 18000),
    'aspire': ('Computing', 'Laptops', 8000, 15000),
    'inspiron': ('Computing', 'Laptops', 12000, 22000),
    'desktop': ('Computing', 'Desktops', 8000, 15000),
    'microtower': ('Computing', 'Desktops', 10000, 18000),
    'imac': ('Computing', 'All-in-One', 25000, 50000),
    'aio': ('Computing', 'All-in-One', 15000, 30000),
    
    # Mobile Devices
    'airpods': ('Mobile', 'Audio Accessories', 800, 1500),
    'iphone': ('Mobile', 'Smartphones', 5000, 15000),
    'samsung': ('Mobile', 'Smartphones', 3000, 12000),
    'nokia': ('Mobile', 'Smartphones', 500, 3000),
    'redmi': ('Mobile', 'Smartphones', 1500, 4000),
    'galaxy': ('Mobile', 'Smartphones', 3000, 12000),
    
    # Gaming
    'ps5': ('Gaming', 'Consoles', 8000, 12000),
    'ps4': ('Gaming', 'Controllers', 600, 1000),
    'nintendo': ('Gaming', 'Consoles', 4000, 8000),
    'gaming': ('Gaming', 'Accessories', 200, 1000),
    'controller': ('Gaming', 'Controllers', 400, 800),
    'dualsense': ('Gaming', 'Controllers', 600, 1000),
    'dualshock': ('Gaming', 'Controllers', 400, 700),
    
    # Audio & Video
    'jbl': ('Audio/Video', 'Speakers', 800, 2000),
    'harman': ('Audio/Video', 'Speakers', 800, 2000),
    'headset': ('Audio/Video', 'Headphones', 300, 1200),
    'headphone': ('Audio/Video', 'Headphones', 200, 1000),
    'microphone': ('Audio/Video', 'Microphones', 150, 600),
    'speaker': ('Audio/Video', 'Speakers', 400, 1500),
    'earbuds': ('Audio/Video', 'Earphones', 200, 800),
    'flip': ('Audio/Video', 'Portable Speakers', 800, 1500),
    'stereo': ('Audio/Video', 'Headphones', 200, 800),
    'wireless': ('Audio/Video', 'Wireless Audio', 300, 1000),
    
    # Networking
    'router': ('Networking', 'Routers', 800, 2000),
    'wifi': ('Networking', 'WiFi Devices', 500, 1500),
    '4g': ('Networking', 'Mobile Internet', 600, 1200),
    'lte': ('Networking', 'Mobile Internet', 600, 1200),
    'tp-link': ('Networking', 'Routers', 500, 1500),
    'd-link': ('Networking', 'Routers', 400, 1200),
    'dlink': ('Networking', 'Routers', 400, 1200),
    
    # Storage
    'ssd': ('Storage', 'Solid State Drives', 400, 1500),
    'hdd': ('Storage', 'Hard Drives', 300, 1000),
    'hard drive': ('Storage', 'Hard Drives', 300, 1000),
    'flash': ('Storage', 'USB Drives', 50, 300),
    'usb': ('Storage', 'USB Drives', 30, 200),
    'sandisk': ('Storage', 'Memory Cards', 100, 500),
    'seagate': ('Storage', 'Hard Drives', 400, 1200),
    'toshiba': ('Storage', 'Hard Drives', 350, 1000),
    'transcend': ('Storage', 'Hard Drives', 500, 1500),
    'lexar': ('Storage', 'SSD', 300, 1000),
    
    # Displays & Monitors
    'display': ('Displays', 'Monitors', 1500, 4000),
    'monitor': ('Displays', 'Monitors', 1200, 3500),
    'tv': ('Displays', 'Televisions', 2000, 8000),
    'akai': ('Displays', 'Televisions', 1800, 4000),
    'bruhm': ('Displays', 'Televisions', 2000, 5000),
    
    # Cables & Adapters
    'cable': ('Accessories', 'Cables', 30, 200),
    'hdmi': ('Accessories', 'Cables', 50, 300),
    'usb': ('Accessories', 'Cables', 20, 150),
    'vga': ('Accessories', 'Cables', 40, 200),
    'adapter': ('Accessories', 'Adapters', 50, 300),
    'converter': ('Accessories', 'Converters', 80, 400),
    'hub': ('Accessories', 'USB Hubs', 150, 600),
    
    # Printers & Office
    'printer': ('Office', 'Printers', 1200, 4000),
    'canon': ('Office', 'Printers', 1000, 3000),
    'laser': ('Office', 'Printers', 1500, 5000),
    'toner': ('Office', 'Printer Supplies', 200, 600),
    'receipt': ('Office', 'POS Equipment', 800, 2000),
    'pos': ('Office', 'POS Equipment', 1500, 5000),
    'cash drawer': ('Office', 'POS Equipment', 1000, 2500),
    'scanner': ('Office', 'Scanners', 500, 1500),
    
    # Photography & Video
    'camera': ('Photography', 'Cameras', 1000, 5000),
    'webcam': ('Photography', 'Web Cameras', 300, 800),
    'tripod': ('Photography', 'Tripods', 200, 800),
    'dji': ('Photography', 'Gimbals', 2000, 5000),
    'osmo': ('Photography', 'Gimbals', 2000, 5000),
    'fujifilm': ('Photography', 'Instant Cameras', 1200, 2500),
    'instax': ('Photography', 'Instant Cameras', 1200, 2500),
    'projector': ('Photography', 'Projectors', 1500, 4000),
    'light': ('Photography', 'Lighting', 200, 800),
    'ring light': ('Photography', 'Lighting', 300, 1000),
    
    # Wearables
    'watch': ('Wearables', 'Smart Watches', 300, 1500),
    'smart watch': ('Wearables', 'Smart Watches', 400, 1500),
    
    # Power & Charging
    'power bank': ('Power', 'Power Banks', 200, 800),
    'charging': ('Power', 'Chargers', 100, 400),
    'socket': ('Power', 'Power Strips', 150, 500),
    
    # Streaming & Media
    'mi tv stick': ('Media', 'Streaming Devices', 400, 800),
    'tv stick': ('Media', 'Streaming Devices', 300, 700),
    
    # Security
    'cctv': ('Security', 'Cameras', 500, 1500),
    'counterfeit': ('Security', 'Detection Equipment', 1500, 3000),
    'money detector': ('Security', 'Detection Equipment', 1500, 3000),
    
    # Input Devices
    'keyboard': ('Input Devices', 'Keyboards', 150, 600),
    'mouse': ('Input Devices', 'Mice', 100, 400),
    'combo': ('Input Devices', 'Keyboard & Mouse', 200, 700),
    'mouse pad': ('Input Devices', 'Mouse Pads', 50, 200),
    
    # Hair Care
    'hair clipper': ('Personal Care', 'Hair Clippers', 200, 600),
    'clipper': ('Personal Care', 'Hair Clippers', 200, 600),
}

def extract_brand_advanced(product_name: str) -> str:
    """Extract brand name using advanced pattern matching."""
    name_lower = product_name.lower()
    
    # Brand patterns
    brand_patterns = {
        'HP': ['hp '],
        'Dell': ['dell '],
        'Acer': ['acer', 'aspire'],
        'Lenovo': ['lenovo'],
        'Canon': ['canon'],
        'Samsung': ['samsung'],
        'Nokia': ['nokia'],
        'Apple': ['airpods', 'iphone', 'imac'],
        'Sony': ['sony'],
        'JBL': ['jbl'],
        'Logitech': ['logitech'],
        'TP-Link': ['tp-link'],
        'D-Link': ['d-link', 'dlink'],
        'Promate': ['promate'],
        'Nintendo': ['nintendo'],
        'DJI': ['dji'],
        'Fujifilm': ['fujifilm'],
        'SanDisk': ['sandisk'],
        'Seagate': ['seagate'],
        'Toshiba': ['toshiba'],
        'Transcend': ['transcend'],
        'Lexar': ['lexar'],
        'Meetion': ['meetion'],
        'Vertux': ['vertux'],
        'ZKTECO': ['zkteco'],
        'Akai': ['akai'],
        'Bruhm': ['bruhm'],
        'Boya': ['boya'],
        'Modio': ['modio'],
        'Redmi': ['redmi'],
        'Pegasus': ['pegasus'],
        'Philips': ['philips'],
        'POStech': ['postech'],
        'Nigachi': ['nigachi'],
        'Imation': ['imation'],
        'Dato': ['dato'],
        'Coopic': ['coopic'],
        'Onyx': ['onyx'],
        'Mi': ['mi tv'],
    }
    
    for brand, patterns in brand_patterns.items():
        if any(pattern in name_lower for pattern in patterns):
            return brand
    
    # Fallback to first word
    words = product_name.split()
    return words[0] if words else "Unknown"

def categorize_product_advanced(product_name: str) -> tuple:
    """Advanced product categorization with price estimation."""
    name_lower = product_name.lower()
    
    # Check each category mapping
    for keyword, (category, subcategory, min_price, max_price) in CATEGORY_MAPPING.items():
        if keyword in name_lower:
            # Estimate price based on category and product specifics
            estimated_price = estimate_price(product_name, min_price, max_price)
            return category, subcategory, estimated_price
    
    # Default category
    return "Electronics", "Other", 500

def estimate_price(product_name: str, min_price: int, max_price: int) -> int:
    """Estimate product price based on name and category range."""
    name_lower = product_name.lower()
    
    # Price modifiers
    premium_keywords = ['pro', 'premium', 'professional', 'gaming', 'wireless', 'smart']
    budget_keywords = ['basic', 'lite', 'mini', 'compact']
    
    base_price = (min_price + max_price) // 2
    
    # Adjust for premium features
    if any(keyword in name_lower for keyword in premium_keywords):
        base_price = int(base_price * 1.3)
    elif any(keyword in name_lower for keyword in budget_keywords):
        base_price = int(base_price * 0.8)
    
    # Capacity/size adjustments
    if 'tb' in name_lower:
        if '4tb' in name_lower:
            base_price = int(base_price * 2.5)
        elif '2tb' in name_lower:
            base_price = int(base_price * 1.8)
        elif '1tb' in name_lower:
            base_price = int(base_price * 1.3)
    elif 'gb' in name_lower:
        if '512gb' in name_lower or '256gb' in name_lower:
            base_price = int(base_price * 1.2)
        elif '128gb' in name_lower:
            base_price = int(base_price * 1.1)
        elif '32gb' in name_lower or '16gb' in name_lower:
            base_price = int(base_price * 0.9)
    
    # Ensure price stays within reasonable bounds
    return max(min_price, min(max_price, base_price))

def generate_detailed_description(product_name: str, category: str, brand: str) -> str:
    """Generate detailed product description."""
    templates = {
        'Computing': f"The {product_name} delivers exceptional computing performance with modern features and reliable build quality. Perfect for both professional work and everyday computing tasks.",
        'Mobile': f"Experience cutting-edge mobile technology with the {product_name}. Featuring advanced capabilities and sleek design for the modern user.",
        'Gaming': f"Elevate your gaming experience with the {product_name}. Designed for serious gamers who demand precision, performance, and reliability.",
        'Audio/Video': f"Immerse yourself in superior sound quality with the {product_name}. Engineered to deliver crystal-clear audio and exceptional performance.",
        'Networking': f"Stay connected with the {product_name}. Featuring fast, reliable networking capabilities for seamless internet connectivity.",
        'Storage': f"Secure and expand your digital storage with the {product_name}. Offering reliable data storage with fast access speeds.",
        'Displays': f"Enhance your visual experience with the {product_name}. Featuring crisp, clear display technology for work and entertainment.",
        'Office': f"Boost your productivity with the {product_name}. Professional-grade equipment designed for efficient office operations.",
        'Photography': f"Capture life's moments with the {product_name}. Professional photography equipment for stunning results.",
        'Wearables': f"Stay connected and track your lifestyle with the {product_name}. Modern wearable technology for the active user.",
    }
    
    return templates.get(category, f"The {product_name} from {brand} offers premium quality and reliable performance for all your technology needs.")

def generate_key_features(product_name: str, category: str) -> str:
    """Generate relevant key features based on product category."""
    feature_sets = {
        'Computing': [
            "High-performance processor",
            "Ample RAM and storage",
            "Modern connectivity options",
            "Energy efficient design",
            "Comprehensive warranty"
        ],
        'Mobile': [
            "Advanced camera system",
            "Long-lasting battery",
            "Fast charging capability",
            "Durable construction",
            "Latest operating system"
        ],
        'Gaming': [
            "Responsive controls",
            "Premium build quality",
            "Ergonomic design",
            "Universal compatibility",
            "Enhanced gaming experience"
        ],
        'Audio/Video': [
            "Superior sound quality",
            "Comfortable design",
            "Wireless connectivity",
            "Long battery life",
            "Noise cancellation"
        ],
        'Networking': [
            "High-speed connectivity",
            "Easy setup and configuration",
            "Reliable performance",
            "Security features",
            "Multiple device support"
        ],
        'Storage': [
            "Fast data transfer speeds",
            "Reliable data protection",
            "Compact design",
            "Universal compatibility",
            "Plug and play operation"
        ],
        'default': [
            "Premium build quality",
            "Reliable performance",
            "Modern design",
            "User-friendly operation",
            "Comprehensive warranty"
        ]
    }
    
    features = feature_sets.get(category, feature_sets['default'])
    return '\n'.join(f"• {feature}" for feature in features)

def create_sku(category: str, subcategory: str, index: int) -> str:
    """Create a meaningful SKU."""
    cat_code = category[:3].upper()
    sub_code = subcategory[:3].upper()
    return f"{cat_code}-{sub_code}-{str(index).zfill(4)}"

def init_database():
    """Initialize SQLite database."""
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            name TEXT NOT NULL,
            brand TEXT,
            category TEXT,
            subcategory TEXT,
            description TEXT,
            features TEXT,
            price_ghs REAL,
            price_usd REAL,
            condition TEXT DEFAULT 'New',
            stock_status TEXT DEFAULT 'In Stock',
            image_path TEXT,
            date_added DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_to_database(products_data):
    """Save products to SQLite database."""
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM products')
    
    for product in products_data:
        cursor.execute('''
            INSERT INTO products (
                sku, name, brand, category, subcategory, description, features,
                price_ghs, price_usd, condition, stock_status, image_path, date_added
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', product)
    
    conn.commit()
    conn.close()

def main():
    """Main function to process all products."""
    print("Enhanced Product Catalog Generator")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Process image files
    products_data = []
    image_thumbnails = []
    
    # Get all image files
    files = sorted(
        [f for f in IMAGE_FOLDER.iterdir() 
         if f.is_file() and f.suffix.lower() in SUPPORTED_EXTS],
        key=lambda p: p.name.lower()
    )
    
    print(f"Found {len(files)} product images")
    
    for index, file in enumerate(files, 1):
        product_name = file.stem
        brand = extract_brand_advanced(product_name)
        category, subcategory, estimated_price = categorize_product_advanced(product_name)
        
        # Generate content
        description = generate_detailed_description(product_name, category, brand)
        features = generate_key_features(product_name, category)
        sku = create_sku(category, subcategory, index)
        date_added = datetime.today().strftime('%Y-%m-%d')
        
        # Calculate USD price
        price_usd = round(estimated_price * USD_RATE, 2)
        
        # Prepare data for Excel
        excel_row = [
            product_name, category, subcategory, brand, description, features,
            "New", estimated_price, price_usd, "In Stock", str(file), sku, date_added
        ]
        
        # Prepare data for database
        db_row = (
            sku, product_name, brand, category, subcategory, description, features,
            estimated_price, price_usd, "New", "In Stock", str(file), date_added
        )
        
        products_data.append((excel_row, db_row))
        
        # Create thumbnail
        try:
            with Image.open(file) as img:
                img.load()
                img.thumbnail((80, 80))
                img_bytes = BytesIO()
                img.save(img_bytes, format="PNG")
                image_thumbnails.append(img_bytes.getvalue())
        except Exception as e:
            print(f"Warning: Could not process image {file}: {e}")
            image_thumbnails.append(None)
        
        if index % 10 == 0:
            print(f"Processed {index} products...")
    
    # Create Excel file
    create_excel_catalog(products_data, image_thumbnails)
    
    # Save to database
    db_data = [item[1] for item in products_data]
    save_to_database(db_data)
    
    # Create JSON export
    create_json_export(products_data)
    
    print(f"\nProcessing complete!")
    print(f"Processed {len(products_data)} products")
    print(f"Excel catalog: {OUTPUT_EXCEL}")
    print(f"Database: {OUTPUT_DB}")
    print(f"JSON export: {OUTPUT_JSON}")

def create_excel_catalog(products_data, image_thumbnails):
    """Create Excel catalog with thumbnails."""
    columns = [
        "Product Name", "Category", "Subcategory", "Brand", "Description", "Key Features",
        "Condition", "Price (GHS)", "Price (USD)", "Stock Status", "File Path", "SKU", "Date Added"
    ]
    
    with xlsxwriter.Workbook(str(OUTPUT_EXCEL)) as workbook:
        worksheet = workbook.add_worksheet("Product Catalog")
        
        # Formats
        header_format = workbook.add_format({
            "bold": True, 
            "bg_color": "#2F75B5", 
            "font_color": "white",
            "border": 1,
            "align": "center"
        })
        wrap_format = workbook.add_format({"text_wrap": True, "valign": "top"})
        price_ghs_format = workbook.add_format({"num_format": '[$GHS] #,##0.00'})
        price_usd_format = workbook.add_format({"num_format": '$#,##0.00'})
        center_format = workbook.add_format({"align": "center", "valign": "vcenter"})
        
        # Write headers
        for col_num, header in enumerate(["Thumbnail"] + columns):
            worksheet.write(0, col_num, header, header_format)
        
        # Freeze header row
        worksheet.freeze_panes(1, 0)
        
        # Write data
        for row_num, ((excel_row, _), img_data) in enumerate(zip(products_data, image_thumbnails), 1):
            # Insert thumbnail
            if img_data:
                worksheet.insert_image(row_num, 0, "thumbnail.png", {
                    "image_data": BytesIO(img_data),
                    "x_scale": 1,
                    "y_scale": 1,
                    "x_offset": 2,
                    "y_offset": 2
                })
            
            worksheet.set_row(row_num, 80)
            
            # Write data columns
            for col_num, value in enumerate(excel_row, 1):
                if col_num in [5, 6]:  # Description, Features
                    worksheet.write(row_num, col_num, value, wrap_format)
                elif col_num == 8:  # Price GHS
                    worksheet.write_number(row_num, col_num, float(value), price_ghs_format)
                elif col_num == 9:  # Price USD
                    worksheet.write_number(row_num, col_num, float(value), price_usd_format)
                elif col_num in [2, 3, 7, 10]:  # Category, Brand, Condition, Stock
                    worksheet.write(row_num, col_num, value, center_format)
                else:
                    worksheet.write(row_num, col_num, value)
        
        # Set column widths
        worksheet.set_column(0, 0, 12)   # Thumbnail
        worksheet.set_column(1, 1, 30)   # Product Name
        worksheet.set_column(2, 4, 18)   # Category, Subcategory, Brand
        worksheet.set_column(5, 6, 45)   # Description, Features
        worksheet.set_column(7, 7, 12)   # Condition
        worksheet.set_column(8, 9, 15)   # Prices
        worksheet.set_column(10, 10, 12) # Stock Status
        worksheet.set_column(11, 11, 35) # File Path
        worksheet.set_column(12, 13, 15) # SKU, Date

def create_json_export(products_data):
    """Create JSON export of products."""
    json_data = []
    
    for excel_row, db_row in products_data:
        product = {
            "sku": db_row[0],
            "name": db_row[1],
            "brand": db_row[2],
            "category": db_row[3],
            "subcategory": db_row[4],
            "description": db_row[5],
            "features": db_row[6].split('\n'),
            "price_ghs": db_row[7],
            "price_usd": db_row[8],
            "condition": db_row[9],
            "stock_status": db_row[10],
            "image_path": db_row[11],
            "date_added": db_row[12]
        }
        json_data.append(product)
    
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
