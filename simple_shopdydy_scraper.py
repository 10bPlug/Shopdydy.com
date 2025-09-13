#!/usr/bin/env python3
"""
Simple ShopDydy.com Product Scraper
===================================

A streamlined version that focuses on extracting and displaying product data
in a clean table format.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
from typing import List, Dict

class SimpleShopDydyScraper:
    def __init__(self):
        self.base_url = "https://shopdydy.com"
        self.products = []
        self.session = requests.Session()
        
        # Headers to appear more like a regular browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session.headers.update(self.headers)
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def clean_price(self, price_text: str) -> float:
        """Extract price from text"""
        if not price_text:
            return None
        
        # Remove everything except digits, dots, and commas
        price_clean = re.sub(r'[^\d.,]', '', price_text.strip())
        
        # Handle different formats
        if ',' in price_clean and '.' in price_clean:
            # Format: 1,234.56
            price_clean = price_clean.replace(',', '')
        elif ',' in price_clean:
            # Could be 1,56 (European) or 1,234 (thousands)
            if len(price_clean.split(',')[-1]) == 2:
                price_clean = price_clean.replace(',', '.')
            else:
                price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except:
            return None
    
    def scrape_homepage(self):
        """Scrape products from the main page"""
        soup = self.get_page(self.base_url)
        if not soup:
            print("❌ Could not access the website")
            return
        
        print("✅ Successfully accessed shopdydy.com")
        
        # Try multiple selectors to find products
        product_selectors = [
            '.product',
            '.product-item',
            '.product-card',
            '.item',
            '[data-product]',
            '.grid-item',
            '.product-grid .product',
            '.products .product'
        ]
        
        products_found = False
        
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"🔍 Found {len(elements)} products using selector: {selector}")
                products_found = True
                
                for element in elements:
                    product = self.extract_product_data(element)
                    if product['name'] or product['price']:
                        self.products.append(product)
                break
        
        if not products_found:
            print("🔍 No products found with standard selectors, trying alternative approach...")
            self.try_alternative_extraction(soup)
    
    def extract_product_data(self, element) -> Dict:
        """Extract product information from a single element"""
        product = {
            'name': '',
            'price': None,
            'original_price': None,
            'description': '',
            'image_url': '',
            'product_url': ''
        }
        
        # Extract name
        name_selectors = ['h1', 'h2', 'h3', '.title', '.name', '.product-title', '.product-name']
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem and name_elem.get_text(strip=True):
                product['name'] = name_elem.get_text(strip=True)
                break
        
        # Extract price
        price_selectors = ['.price', '.cost', '.amount', '.money', '[data-price]']
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price = self.clean_price(price_elem.get_text(strip=True))
                if price:
                    product['price'] = price
                    break
        
        # Extract original price (for sales)
        original_price_selectors = ['.original-price', '.regular-price', '.was-price', '.old-price']
        for selector in original_price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                original_price = self.clean_price(price_elem.get_text(strip=True))
                if original_price:
                    product['original_price'] = original_price
                    break
        
        # Extract description
        desc_elem = element.select_one('.description, .product-description, .summary')
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if len(desc_text) > 10:
                product['description'] = desc_text[:200] + '...' if len(desc_text) > 200 else desc_text
        
        # Extract image URL
        img_elem = element.select_one('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src')
            if src:
                product['image_url'] = urljoin(self.base_url, src)
        
        # Extract product URL
        link_elem = element.select_one('a')
        if link_elem:
            href = link_elem.get('href')
            if href:
                product['product_url'] = urljoin(self.base_url, href)
        
        return product
    
    def try_alternative_extraction(self, soup):
        """Try alternative methods to find products"""
        # Look for any elements with price-like text
        all_elements = soup.find_all(text=re.compile(r'[\$£€]\d+|USD|EUR|GBP|\d+\.\d{2}'))
        
        if all_elements:
            print(f"🔍 Found {len(all_elements)} elements with price-like text")
            
            for text in all_elements[:10]:  # Limit to first 10
                parent = text.parent
                if parent:
                    product = self.extract_product_data(parent)
                    if product['name'] or product['price']:
                        self.products.append(product)
        else:
            # Create a sample entry to show the structure
            sample_product = {
                'name': 'Sample Product (Website structure not recognized)',
                'price': 0.00,
                'original_price': None,
                'description': 'Unable to automatically detect products. Manual inspection needed.',
                'image_url': '',
                'product_url': self.base_url
            }
            self.products.append(sample_product)
    
    def display_results(self):
        """Display results in a formatted table"""
        if not self.products:
            print("❌ No products found")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.products)
        
        # Clean up the data
        df = df.fillna('')
        
        # Format prices
        def format_price(price):
            if price and price != 0:
                return f"${price:.2f}"
            return "N/A"
        
        if 'price' in df.columns:
            df['formatted_price'] = df['price'].apply(format_price)
        if 'original_price' in df.columns:
            df['formatted_original_price'] = df['original_price'].apply(format_price)
        
        # Display table
        print("\n" + "="*120)
        print("🛍️  SHOPDYDY.COM PRODUCT CATALOG")
        print("="*120)
        
        # Select columns to display
        display_cols = ['name', 'formatted_price']
        if 'formatted_original_price' in df.columns:
            display_cols.append('formatted_original_price')
        display_cols.extend(['description'])
        
        available_cols = [col for col in display_cols if col in df.columns and not df[col].isna().all()]
        
        if available_cols:
            display_df = df[available_cols].copy()
            
            # Rename columns for better display
            column_names = {
                'name': 'Product Name',
                'formatted_price': 'Price',
                'formatted_original_price': 'Original Price',
                'description': 'Description'
            }
            display_df = display_df.rename(columns=column_names)
            
            print(display_df.to_string(index=False, max_colwidth=60))
        else:
            print("No displayable data found")
        
        print("="*120)
        print(f"📊 Total Products Found: {len(self.products)}")
        
        # Show summary statistics
        if 'price' in df.columns:
            prices = df['price'].dropna()
            if len(prices) > 0:
                print(f"💰 Price Range: ${prices.min():.2f} - ${prices.max():.2f}")
                print(f"📈 Average Price: ${prices.mean():.2f}")
        
        print("="*120)
    
    def save_to_csv(self, filename='shopdydy_products.csv'):
        """Save products to CSV"""
        if not self.products:
            print("No products to save")
            return
        
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
    
    def run(self):
        """Main execution method"""
        print("🚀 Starting ShopDydy.com Product Scraper")
        print("-" * 50)
        
        # Scrape the website
        self.scrape_homepage()
        
        # Display results
        self.display_results()
        
        # Save to file
        if self.products:
            self.save_to_csv()
        
        print("\n✅ Scraping completed!")

def main():
    scraper = SimpleShopDydyScraper()
    scraper.run()

if __name__ == "__main__":
    main()