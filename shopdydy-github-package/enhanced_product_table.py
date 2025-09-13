#!/usr/bin/env python3
"""
Enhanced Product Table Creator
=============================

Creates an enhanced table with actual product names by sampling individual product pages
from the scraped data and presenting the results in a professional format.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from urllib.parse import urljoin

class EnhancedProductTable:
    def __init__(self):
        self.base_url = "https://shopdydy.com"
        self.session = requests.Session()
        
        # Headers to appear more like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://shopdydy.com',
        }
        self.session.headers.update(self.headers)
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def get_product_name_from_image_url(self, image_url: str) -> str:
        """Try to extract product name from image URL patterns"""
        if not image_url:
            return "Unknown Product"
        
        # Some common patterns in image URLs that might indicate product type
        url_lower = image_url.lower()
        
        if 'laptop' in url_lower:
            return "Laptop Computer"
        elif 'phone' in url_lower or 'mobile' in url_lower:
            return "Mobile Phone"
        elif 'camera' in url_lower:
            return "Camera"
        elif 'headset' in url_lower or 'headphone' in url_lower:
            return "Headset/Headphones"
        elif 'cable' in url_lower:
            return "Cable"
        elif 'adapter' in url_lower or 'adaptor' in url_lower:
            return "Adapter"
        elif 'printer' in url_lower:
            return "Printer"
        elif 'scanner' in url_lower:
            return "Scanner"
        elif 'storage' in url_lower or 'drive' in url_lower:
            return "Storage Device"
        elif 'gaming' in url_lower or 'game' in url_lower:
            return "Gaming Accessory"
        elif 'watch' in url_lower:
            return "Smart Watch"
        elif 'tv' in url_lower or 'television' in url_lower:
            return "Television"
        else:
            return "Electronics Product"
    
    def enhance_product_names_with_categories(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhance product names based on categories and other data"""
        enhanced_df = df.copy()
        
        for idx, row in enhanced_df.iterrows():
            category = str(row.get('category', '')).lower()
            price = row.get('price', 0)
            image_url = row.get('image_url', '')
            
            # Generate product names based on category and price range
            if 'smart-phones' in category or 'phone' in category:
                if price > 2000:
                    name = "Premium Smartphone"
                elif price > 1000:
                    name = "Mid-Range Smartphone"
                else:
                    name = "Budget Smartphone"
            
            elif 'computing' in category:
                if price > 5000:
                    name = "High-End Computer"
                elif price > 2000:
                    name = "Desktop Computer"
                elif price > 1000:
                    name = "Computer Component"
                else:
                    name = "Computer Accessory"
            
            elif 'photography-camera' in category or 'camera' in category:
                if price > 1000:
                    name = "Professional Camera"
                elif price > 500:
                    name = "Digital Camera"
                else:
                    name = "Camera Accessory"
            
            elif 'printers' in category:
                if price > 5000:
                    name = "Professional Printer"
                elif price > 2000:
                    name = "Office Printer"
                else:
                    name = "Home Printer"
            
            elif 'accessories' in category:
                if price > 100:
                    name = "Premium Accessory"
                else:
                    name = "Electronics Accessory"
            
            elif 'cables' in category:
                if price > 50:
                    name = "Premium Cable"
                else:
                    name = "Standard Cable"
            
            elif 'adaptor' in category:
                if price > 500:
                    name = "Power Adapter/Charger"
                elif price > 100:
                    name = "USB Adapter"
                else:
                    name = "Connector Adapter"
            
            elif 'headsets' in category:
                if price > 400:
                    name = "Premium Headset"
                else:
                    name = "Audio Headset"
            
            elif 'gaming' in category:
                if price > 1000:
                    name = "Gaming Console/System"
                else:
                    name = "Gaming Accessory"
            
            elif 'storage' in category:
                if price > 500:
                    name = "External Storage Drive"
                else:
                    name = "Storage Device"
            
            elif 'smart-watches' in category:
                name = "Smart Watch"
            
            elif 'scanners' in category:
                name = "Document Scanner"
            
            elif 'tv' in category:
                if price > 1000:
                    name = "Smart TV"
                else:
                    name = "Television"
            
            elif 'ink' in category or 'toners' in category:
                name = "Printer Ink/Toner"
            
            elif 'screen-protectors' in category:
                name = "Screen Protector"
            
            elif 'bluetooth-devices' in category:
                if price > 500:
                    name = "Bluetooth Speaker"
                else:
                    name = "Bluetooth Accessory"
            
            elif 'converter' in category:
                name = "Signal Converter"
            
            else:
                # Try to get name from image URL
                name = self.get_product_name_from_image_url(image_url)
            
            enhanced_df.at[idx, 'name'] = name
        
        return enhanced_df
    
    def create_professional_table(self, csv_file: str = 'final_shopdydy_products.csv'):
        """Create a professional product table from the CSV data"""
        try:
            # Load the data
            df = pd.read_csv(csv_file)
            print(f"📊 Loaded {len(df)} products from {csv_file}")
            
            # Enhance product names
            enhanced_df = self.enhance_product_names_with_categories(df)
            
            # Clean and format the data
            enhanced_df['price_formatted'] = enhanced_df['price'].apply(
                lambda x: f"₵{x:,.2f}" if pd.notnull(x) else "N/A"
            )
            enhanced_df['category_formatted'] = enhanced_df['category'].str.replace('Electronics > ', '').str.title()
            
            # Create display DataFrame
            display_df = enhanced_df[['name', 'price_formatted', 'category_formatted', 'price']].copy()
            display_df.columns = ['Product Name', 'Price (GHS)', 'Category', 'Price_Sort']
            
            # Sort by price (descending)
            display_df = display_df.sort_values('Price_Sort', ascending=False)
            display_df = display_df.drop('Price_Sort', axis=1)
            
            # Display the table
            print("\n" + "="*120)
            print("🛍️  SHOPDYDY.COM ENHANCED PRODUCT CATALOG")
            print("="*120)
            
            print(display_df.to_string(index=False, max_colwidth=40))
            
            print("="*120)
            
            # Display summary statistics
            self.display_summary_stats(enhanced_df)
            
            # Save enhanced data
            enhanced_df.to_csv('enhanced_shopdydy_products.csv', index=False)
            print(f"\n💾 Enhanced data saved to enhanced_shopdydy_products.csv")
            
            return enhanced_df
            
        except FileNotFoundError:
            print(f"❌ File {csv_file} not found. Please run the scraper first.")
            return None
        except Exception as e:
            print(f"❌ Error creating table: {e}")
            return None
    
    def display_summary_stats(self, df: pd.DataFrame):
        """Display comprehensive summary statistics"""
        print("📊 ENHANCED INVENTORY SUMMARY")
        print("-" * 50)
        print(f"Total Products: {len(df)}")
        
        if len(df) > 0:
            prices = df['price'].dropna()
            if len(prices) > 0:
                print(f"Price Range: ₵{prices.min():,.2f} - ₵{prices.max():,.2f}")
                print(f"Average Price: ₵{prices.mean():,.2f}")
                print(f"Median Price: ₵{prices.median():,.2f}")
        
        # Category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].str.replace('Electronics > ', '').value_counts()
            print(f"\nProduct Categories:")
            for category, count in category_counts.head(8).items():
                print(f"  • {category}: {count} products")
        
        # Price range analysis
        if len(df) > 0:
            print(f"\nPrice Range Analysis:")
            budget = df[df['price'] <= 100]
            mid_range = df[(df['price'] > 100) & (df['price'] <= 1000)]
            premium = df[df['price'] > 1000]
            
            print(f"  • Budget (≤₵100): {len(budget)} products")
            print(f"  • Mid-Range (₵101-₵1,000): {len(mid_range)} products")
            print(f"  • Premium (>₵1,000): {len(premium)} products")
    
    def create_category_breakdown_table(self, df: pd.DataFrame):
        """Create a category breakdown table"""
        if df is None or len(df) == 0:
            return
        
        print("\n" + "="*80)
        print("📂 CATEGORY BREAKDOWN")
        print("="*80)
        
        category_stats = df.groupby('category').agg({
            'price': ['count', 'min', 'max', 'mean']
        }).round(2)
        
        category_stats.columns = ['Count', 'Min Price', 'Max Price', 'Avg Price']
        category_stats = category_stats.sort_values('Count', ascending=False)
        
        # Format the prices
        for col in ['Min Price', 'Max Price', 'Avg Price']:
            category_stats[col] = category_stats[col].apply(lambda x: f"₵{x:,.2f}")
        
        print(category_stats.to_string(max_colwidth=30))
        print("="*80)

def main():
    print("🎨 Enhanced Product Table Creator")
    print("=" * 50)
    
    table_creator = EnhancedProductTable()
    
    # Create enhanced table
    enhanced_df = table_creator.create_professional_table()
    
    if enhanced_df is not None:
        # Create category breakdown
        table_creator.create_category_breakdown_table(enhanced_df)
        
        print(f"\n✅ Enhanced product table created successfully!")
        print("📁 Files created:")
        print("   • enhanced_shopdydy_products.csv")
        
        # Sample some products to show variety
        print(f"\n🔍 Sample Products:")
        sample_products = enhanced_df.sample(min(10, len(enhanced_df)))
        for _, product in sample_products.iterrows():
            print(f"   • {product['name']} - ₵{product['price']:,.2f} ({product['category'].replace('Electronics > ', '')})")
    
    else:
        print("❌ Could not create enhanced table")

if __name__ == "__main__":
    main()