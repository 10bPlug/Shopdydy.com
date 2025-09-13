#!/usr/bin/env python3
"""
Web-based Product Catalog Viewer for Shopdydy.com
Flask application to view and manage the product database.
"""

import os
import sqlite3
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import base64

# Configuration
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "products.db"
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
# Use environment-provided secret for sessions; fall back to a random key in dev
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') or os.environ.get('SECRET_KEY') or base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload folder exists
UPLOAD_FOLDER.mkdir(exist_ok=True)

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_base64(image_path):
    """Convert image to base64 for display."""
    try:
        if os.path.exists(image_path):
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
    except Exception:
        pass
    return None

@app.context_processor
def inject_current_date():
    """Inject the current date (UTC) for templates."""
    from datetime import datetime
    return {"current_date": datetime.utcnow().strftime('%Y-%m-%d')}

@app.route('/')
def index():
    """Main catalog page."""
    conn = get_db_connection()
    
    # Get filter parameters
    category = request.args.get('category', '')
    brand = request.args.get('brand', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'name')
    sort_order = request.args.get('order', 'asc')
    
    # Build query
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    
    if search:
        query += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    # Add sorting
    valid_sort_columns = ['name', 'brand', 'category', 'price_ghs', 'date_added']
    if sort_by in valid_sort_columns:
        query += f" ORDER BY {sort_by}"
        if sort_order == 'desc':
            query += " DESC"
    
    products = conn.execute(query, params).fetchall()
    
    # Get filter options
    categories = conn.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    brands = conn.execute("SELECT DISTINCT brand FROM products ORDER BY brand").fetchall()
    
    conn.close()
    
    # Add image data to products
    products_with_images = []
    for product in products:
        product_dict = dict(product)
        product_dict['image_data'] = get_image_base64(product['image_path'])
        products_with_images.append(product_dict)
    
    return render_template('catalog.html', 
                         products=products_with_images,
                         categories=categories,
                         brands=brands,
                         current_category=category,
                         current_brand=brand,
                         current_search=search,
                         current_sort=sort_by,
                         current_order=sort_order)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page."""
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    conn.close()
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('index'))
    
    product_dict = dict(product)
    product_dict['image_data'] = get_image_base64(product['image_path'])
    product_dict['features_list'] = product['features'].split('\n') if product['features'] else []
    
    return render_template('product_detail.html', product=product_dict)

@app.route('/api/products')
def api_products():
    """API endpoint for products."""
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        product_dict = dict(product)
        product_dict['image_data'] = get_image_base64(product['image_path'])
        products_list.append(product_dict)
    
    return jsonify(products_list)

@app.route('/api/stats')
def api_stats():
    """API endpoint for catalog statistics."""
    conn = get_db_connection()
    
    stats = {
        'total_products': conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
        'total_categories': conn.execute("SELECT COUNT(DISTINCT category) FROM products").fetchone()[0],
        'total_brands': conn.execute("SELECT COUNT(DISTINCT brand) FROM products").fetchone()[0],
        'total_value_ghs': conn.execute("SELECT SUM(price_ghs) FROM products").fetchone()[0] or 0,
        'avg_price_ghs': conn.execute("SELECT AVG(price_ghs) FROM products").fetchone()[0] or 0
    }
    
    # Category breakdown
    category_stats = conn.execute("""
        SELECT category, COUNT(*) as count, AVG(price_ghs) as avg_price 
        FROM products 
        GROUP BY category 
        ORDER BY count DESC
    """).fetchall()
    
    stats['categories'] = [dict(cat) for cat in category_stats]
    
    conn.close()
    return jsonify(stats)

@app.template_filter('currency')
def currency_filter(value):
    """Format currency values."""
    try:
        return f"GHS {float(value):,.2f}"
    except (ValueError, TypeError):
        return "GHS 0.00"

@app.template_filter('usd_currency')
def usd_currency_filter(value):
    """Format USD currency values."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

if __name__ == '__main__':
    # Check if database exists
    if not DB_PATH.exists():
        print("Database not found. Please run enhanced_product_catalog.py first.")
        exit(1)
    
    print("Starting Shopdydy Product Catalog Web Interface...")
    print(f"Database: {DB_PATH}")
    print("Open your browser to: http://localhost:5000")
    
    # Respect DEBUG from environment; default to False for safety
    debug_mode = os.environ.get('FLASK_DEBUG', '').strip() in {'1', 'true', 'True'}
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
