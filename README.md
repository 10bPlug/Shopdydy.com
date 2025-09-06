# Shopdydy Product Catalog System

A comprehensive product catalog system that automatically generates product databases from image files. The system analyzes product images, categorizes them intelligently, estimates prices, and creates multiple output formats for easy viewing and management.

## 🌟 Features

- **Intelligent Product Categorization**: Automatically categorizes products based on filename analysis
- **Smart Price Estimation**: Estimates prices based on product category and features
- **Brand Recognition**: Extracts brand names from product filenames
- **Multiple Output Formats**: Generates SQLite database, JSON, CSV, and Excel files
- **Web Interface**: Beautiful HTML catalog viewer with search and filtering
- **Comprehensive Product Data**: Generates descriptions, features, SKUs, and more

## 📁 Generated Files

After running the catalog generator, you'll find these files:

- `products.db` - SQLite database with all product information
- `products.json` - JSON export for API integration
- `products.csv` - CSV file for spreadsheet applications
- `product_catalog.xlsx` - Excel file with thumbnails (if xlsxwriter is available)
- `catalog_viewer.html` - Standalone HTML catalog viewer

## 🚀 Quick Start

### Option 1: Simple Catalog (No Dependencies)
```bash
python3 simple_catalog.py
```

### Option 2: Enhanced Catalog (Requires Dependencies)
```bash
# Install dependencies first
pip install -r requirements.txt

# Run enhanced catalog generator
python3 enhanced_product_catalog.py
```

### Option 3: Web Interface (Requires Flask)
```bash
# Install Flask
pip install flask

# Run web interface
python3 web_catalog.py
```

## 📊 Catalog Statistics

The system has processed **137 product images** and generated:

- **14 Categories**: Computing, Mobile, Gaming, Audio/Video, Networking, Storage, Displays, Accessories, Office, Photography, Wearables, Power, Media, Security, Input Devices, Personal Care
- **81 Brands**: HP, Promate, Logitech, Meetion, Apple, Samsung, Nokia, Sony, JBL, Canon, and many more
- **Total Catalog Value**: GHS 460,578.00
- **Average Product Price**: GHS 3,361.88

### Top Categories by Product Count:
1. **Storage** - 28 products
2. **Audio/Video** - 19 products  
3. **Computing** - 18 products
4. **Accessories** - 11 products
5. **Photography** - 11 products

### Top Brands by Product Count:
1. **HP** - 13 products
2. **Promate** - 12 products
3. **Logitech** - 5 products
4. **Meetion** - 4 products
5. **Apple** - 3 products

## 🔧 System Architecture

### Product Classification System

The system uses an intelligent categorization engine that:

1. **Analyzes Product Names**: Extracts keywords and patterns from filenames
2. **Maps to Categories**: Uses a comprehensive mapping of keywords to product categories
3. **Estimates Prices**: Applies price ranges based on category and product features
4. **Generates Content**: Creates descriptions, features, and specifications

### Database Schema

```sql
CREATE TABLE products (
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
);
```

## 🎨 Web Interface Features

The HTML catalog viewer (`catalog_viewer.html`) provides:

- **Search Functionality**: Search by name, brand, or description
- **Advanced Filtering**: Filter by category and brand
- **Sorting Options**: Sort by name, brand, category, price, or date
- **Product Details**: Modal view with comprehensive product information
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Statistics Dashboard**: Overview of catalog metrics
- **No Server Required**: Pure client-side HTML/JavaScript

## 📱 Viewing the Catalog

### Method 1: HTML Viewer (Recommended)
1. Open `catalog_viewer.html` in any modern web browser
2. The viewer will automatically load product data from `products.json`
3. Use search, filters, and sorting to explore products
4. Click on any product to view detailed information

### Method 2: JSON API
Access the `products.json` file directly for API integration:
```javascript
// Example: Load products in your application
fetch('products.json')
  .then(response => response.json())
  .then(products => {
    console.log('Loaded', products.length, 'products');
  });
```

### Method 3: Database Access
Query the SQLite database directly:
```python
import sqlite3

conn = sqlite3.connect('products.db')
cursor = conn.cursor()

# Get all products
products = cursor.execute("SELECT * FROM products").fetchall()

# Search products
results = cursor.execute(
    "SELECT * FROM products WHERE name LIKE ? OR brand LIKE ?", 
    ('%laptop%', '%HP%')
).fetchall()
```

## 🛠️ Customization

### Adding New Categories
Edit the `CATEGORY_MAPPING` dictionary in the Python scripts to add new product categories:

```python
CATEGORY_MAPPING = {
    'new_keyword': ('Category', 'Subcategory', min_price, max_price),
    # Add more mappings...
}
```

### Modifying Price Estimation
Adjust price ranges and modifiers in the `estimate_price()` function:

```python
def estimate_price(product_name: str, min_price: int, max_price: int) -> int:
    # Customize price estimation logic here
    pass
```

### Brand Recognition
Add new brand patterns in the `extract_brand_advanced()` function:

```python
brand_patterns = {
    'New Brand': ['keyword1', 'keyword2'],
    # Add more brand patterns...
}
```

## 📋 Requirements

### Minimal Requirements (simple_catalog.py)
- Python 3.6+
- Built-in libraries only (sqlite3, json, csv, pathlib)

### Enhanced Features
- `Pillow` - Image processing for thumbnails
- `xlsxwriter` - Excel file generation with images
- `Flask` - Web interface (optional)

## 🔍 Troubleshooting

### Common Issues

1. **"No module named 'xlsxwriter'"**
   - Solution: Use `simple_catalog.py` instead, or install dependencies

2. **Images not showing in HTML viewer**
   - Ensure image files are in the same directory as the HTML file
   - Check that image paths in `products.json` are correct

3. **JSON file not loading**
   - Make sure `products.json` is in the same directory as `catalog_viewer.html`
   - Check browser console for error messages

### Performance Notes

- The system can handle hundreds of products efficiently
- Large image files may slow down processing
- Consider optimizing images for web viewing

## 🚀 Future Enhancements

Potential improvements for the system:

- **Image Processing**: Automatic image optimization and thumbnail generation
- **Inventory Management**: Stock tracking and low inventory alerts
- **Price Updates**: Dynamic pricing based on market conditions
- **Multi-language Support**: Internationalization for global markets
- **Advanced Search**: Full-text search with relevance scoring
- **Export Options**: Additional export formats (PDF catalogs, etc.)

## 📄 File Structure

```
Shopdydy.com/
├── README.md                     # This file
├── simple_catalog.py            # Main catalog generator (no dependencies)
├── enhanced_product_catalog.py  # Enhanced version with Excel support
├── web_catalog.py              # Flask web interface
├── catalog_viewer.html         # Standalone HTML viewer
├── requirements.txt            # Python dependencies
├── products.db                 # Generated SQLite database
├── products.json              # Generated JSON export
├── products.csv               # Generated CSV export
├── product/                   # Product images folder
│   ├── [137 product images].png
│   └── ...
└── templates/                 # Flask templates (if using web interface)
    ├── base.html
    ├── catalog.html
    └── product_detail.html
```

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support or questions about the catalog system:

- Check the troubleshooting section above
- Review the generated files for data accuracy
- Verify image files are properly named and accessible

---

**Generated by Shopdydy Product Catalog System** - Your trusted technology partner
