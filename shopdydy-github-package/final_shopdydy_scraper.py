#!/usr/bin/env python3
"""
Final ShopDydy.com Product Scraper
==================================

An optimized scraper that properly extracts product names, prices, and details
from shopdydy.com and presents them in a professional table format.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin
from typing import List, Dict
import json

class FinalShopDydyScraper:
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
            'Referer': 'https://shopdydy.com',
        }
        self.session.headers.update(self.headers)
    
    def get_page(self, url: str) -> BeautifulSoup:
        """Fetch and parse a web page"""
        try:
            print(f"🔍 Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def clean_price(self, price_text: str) -> float:
        """Extract price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and extract numbers
        price_clean = re.sub(r'[^\d.,]', '', price_text.strip())
        
        if ',' in price_clean and '.' in price_clean:
            price_clean = price_clean.replace(',', '')
        elif ',' in price_clean:
            if len(price_clean.split(',')[-1]) == 2:
                price_clean = price_clean.replace(',', '.')
            else:
                price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except:
            return None
    
    def get_product_categories(self) -> List[str]:
        """Get all product category URLs"""
        soup = self.get_page(self.base_url)
        if not soup:
            return []
        
        category_urls = []
        
        # Look for category links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if '/category/' in href:
                full_url = urljoin(self.base_url, href)
                if full_url not in category_urls:
                    category_urls.append(full_url)
        
        return category_urls
    
    def extract_product_from_item(self, item_element, page_url: str) -> Dict:
        """Extract product information from a single item element"""
        product = {
            'name': 'Unknown Product',
            'price': None,
            'description': '',
            'image_url': '',
            'product_url': page_url,
            'category': ''
        }
        
        # Extract product URL and name from link
        link = item_element.select_one('a')
        if link:
            href = link.get('href', '')
            if href:
                product['product_url'] = urljoin(self.base_url, href)
                
                # Try to get product name from link title or text
                title = link.get('title', '').strip()
                if title:
                    product['name'] = title
                else:
                    # Get text from the link, but avoid price text
                    link_text = link.get_text(strip=True)
                    # Remove price-like patterns from the text
                    name_text = re.sub(r'₵\d+|GHS\s*\d+|\$\d+', '', link_text).strip()
                    if name_text and len(name_text) > 2:
                        product['name'] = name_text
        
        # If we still don't have a good name, try image alt text
        if product['name'] == 'Unknown Product' or len(product['name']) < 3:
            img = item_element.select_one('img')
            if img:
                alt_text = img.get('alt', '').strip()
                if alt_text and len(alt_text) > 2:
                    product['name'] = alt_text
        
        # Extract price
        price_element = item_element.select_one('.price, .cost, .amount, [data-price]')
        if price_element:
            price_text = price_element.get_text(strip=True)
            product['price'] = self.clean_price(price_text)
        else:
            # Look for price in any text that looks like currency
            all_text = item_element.get_text()
            price_matches = re.findall(r'₵(\d+(?:,\d{3})*(?:\.\d{2})?)', all_text)
            if price_matches:
                product['price'] = self.clean_price(price_matches[0])
        
        # Extract image URL
        img = item_element.select_one('img')
        if img:
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                product['image_url'] = urljoin(self.base_url, src)
        
        # Extract category from URL
        if '/category/' in page_url:
            category_part = page_url.split('/category/')[-1]
            product['category'] = category_part.replace('/', ' > ').replace('-', ' ').title()
        
        return product
    
    def get_product_details(self, product_url: str) -> Dict:
        """Get detailed product information from individual product page"""
        soup = self.get_page(product_url)
        if not soup:
            return {}
        
        details = {}
        
        # Try to get better product name from product page
        name_selectors = [
            'h1.product-title',
            'h1',
            '.product-name',
            '.product-title',
            '[data-product-title]'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if name and len(name) > 3:
                    details['name'] = name
                    break
        
        # Try to get better description
        desc_selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info p',
            '.details'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc = element.get_text(strip=True)
                if desc and len(desc) > 10:
                    details['description'] = desc[:300] + '...' if len(desc) > 300 else desc
                    break
        
        return details
    
    def scrape_category(self, category_url: str) -> List[Dict]:
        """Scrape all products from a category page"""
        soup = self.get_page(category_url)
        if not soup:
            return []
        
        products = []
        
        # Find all product items
        items = soup.select('.item')
        print(f"  📦 Found {len(items)} items in this category")
        
        for item in items:
            product = self.extract_product_from_item(item, category_url)
            
            # Try to get more details from individual product page
            if product['product_url'] != category_url and product['name'] == 'Unknown Product':
                details = self.get_product_details(product['product_url'])
                product.update(details)
            
            if product['price'] is not None:  # Only add if we have a price
                products.append(product)
                print(f"    ✅ {product['name']} - ₵{product['price']}")
        
        return products
    
    def scrape_all_products(self) -> List[Dict]:
        """Main method to scrape all products"""
        print("🛍️  Final ShopDydy.com Product Scraper")
        print("=" * 60)
        print("🚀 Starting comprehensive product scraping...")
        
        # Get all category URLs
        categories = self.get_product_categories()
        print(f"📂 Found {len(categories)} categories to scrape")
        
        all_products = []
        
        for i, category_url in enumerate(categories, 1):
            print(f"\n📂 Scraping category {i}/{len(categories)}")
            print(f"   {category_url}")
            
            products = self.scrape_category(category_url)
            all_products.extend(products)
            
            # Be respectful - add delay between requests
            time.sleep(1)
        
        # Remove duplicates based on name and price
        unique_products = []
        seen = set()
        
        for product in all_products:
            # Create a key for deduplication
            key = (product['name'].lower().strip(), product['price'])
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        self.products = unique_products
        print(f"\n🎉 Scraping completed! Found {len(self.products)} unique products")
        return self.products
    
    def create_professional_table(self):
        """Create and display a professional product table"""
        if not self.products:
            print("❌ No products found")
            return
        
        # Create DataFrame
        df = pd.DataFrame(self.products)
        
        # Clean and format the data
        df['name'] = df['name'].str.strip()
        df['price_formatted'] = df['price'].apply(lambda x: f"₵{x:,.2f}" if x else "N/A")
        df['category'] = df['category'].fillna('General')
        df['description'] = df['description'].fillna('')
        
        # Truncate long names and descriptions for better display
        df['display_name'] = df['name'].apply(
            lambda x: (x[:40] + '...') if len(str(x)) > 40 else x
        )
        df['display_description'] = df['description'].apply(
            lambda x: (x[:60] + '...') if len(str(x)) > 60 else x
        )
        
        # Create display table
        display_df = df[['display_name', 'price_formatted', 'category', 'display_description']].copy()
        display_df.columns = ['Product Name', 'Price (GHS)', 'Category', 'Description']
        
        # Sort by price (descending)
        display_df = display_df.sort_values('Price (GHS)', ascending=False)
        
        # Display the table
        print("\n" + "="*120)
        print("🛍️  SHOPDYDY.COM PRODUCT CATALOG - COMPLETE INVENTORY")
        print("="*120)
        
        print(display_df.to_string(index=False, max_colwidth=50))
        
        print("="*120)
        
        # Display summary statistics
        print("📊 INVENTORY SUMMARY")
        print("-" * 50)
        print(f"Total Products: {len(self.products)}")
        
        if len(df) > 0:
            prices = df['price'].dropna()
            if len(prices) > 0:
                print(f"Price Range: ₵{prices.min():,.2f} - ₵{prices.max():,.2f}")
                print(f"Average Price: ₵{prices.mean():,.2f}")
                print(f"Median Price: ₵{prices.median():,.2f}")
        
        # Category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            print(f"\nTop Categories:")
            for category, count in category_counts.head(5).items():
                print(f"  • {category}: {count} products")
        
        print("="*120)
    
    def save_to_files(self):
        """Save products to both CSV and JSON files"""
        if not self.products:
            print("No products to save")
            return
        
        # Save to CSV
        df = pd.DataFrame(self.products)
        df.to_csv('final_shopdydy_products.csv', index=False)
        print(f"💾 Data saved to final_shopdydy_products.csv")
        
        # Save to JSON
        with open('final_shopdydy_products.json', 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to final_shopdydy_products.json")
        
        # Create a summary report
        df = pd.DataFrame(self.products)
        summary = {
            'total_products': len(self.products),
            'categories': df['category'].nunique() if 'category' in df.columns else 0,
            'price_range': {
                'min': float(df['price'].min()) if len(df) > 0 else 0,
                'max': float(df['price'].max()) if len(df) > 0 else 0,
                'average': float(df['price'].mean()) if len(df) > 0 else 0
            },
            'scraping_timestamp': pd.Timestamp.now().isoformat()
        }
        
        with open('shopdydy_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"📋 Summary report saved to shopdydy_summary.json")

def main():
    scraper = FinalShopDydyScraper()
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Display professional table
            scraper.create_professional_table()
            
            # Save to files
            scraper.save_to_files()
            
            print(f"\n✅ Mission accomplished!")
            print(f"📦 Successfully scraped {len(products)} products from ShopDydy.com")
            print("📁 Files created:")
            print("   • final_shopdydy_products.csv")
            print("   • final_shopdydy_products.json") 
            print("   • shopdydy_summary.json")
            
        else:
            print("\n❌ No products found")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()