#!/usr/bin/env python3
"""
Comprehensive ShopDydy.com Product Scraper
==========================================

An enhanced scraper that explores multiple pages and uses various techniques
to find all available products on shopdydy.com
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from typing import List, Dict, Set
import json

class ComprehensiveShopDydyScraper:
    def __init__(self):
        self.base_url = "https://shopdydy.com"
        self.products = []
        self.visited_urls = set()
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
        if url in self.visited_urls:
            return None
            
        try:
            print(f"🔍 Fetching: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            self.visited_urls.add(url)
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
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
    
    def find_all_pages(self) -> List[str]:
        """Discover all possible pages that might contain products"""
        pages_to_check = []
        
        # Start with the main page
        soup = self.get_page(self.base_url)
        if not soup:
            print("❌ Could not access main website")
            return []
        
        print("✅ Successfully accessed shopdydy.com")
        
        # Common e-commerce paths
        common_paths = [
            '/',
            '/products',
            '/shop',
            '/catalog',
            '/store',
            '/collections',
            '/categories',
            '/items',
            '/browse',
            '/all-products'
        ]
        
        # Add common paths
        for path in common_paths:
            pages_to_check.append(urljoin(self.base_url, path))
        
        # Look for navigation links
        nav_links = soup.find_all('a', href=True)
        for link in nav_links:
            href = link.get('href', '')
            full_url = urljoin(self.base_url, href)
            
            # Check if it looks like a category or product listing page
            if any(keyword in href.lower() for keyword in ['product', 'category', 'collection', 'shop', 'catalog', 'item']):
                if full_url not in pages_to_check:
                    pages_to_check.append(full_url)
        
        # Look for pagination links
        pagination_links = soup.select('a[href*="page"], a[href*="p="], .pagination a, .pager a')
        for link in pagination_links:
            href = link.get('href', '')
            full_url = urljoin(self.base_url, href)
            if full_url not in pages_to_check:
                pages_to_check.append(full_url)
        
        # Try to find API endpoints or AJAX calls (look in script tags)
        scripts = soup.find_all('script')
        for script in scripts:
            script_content = script.string or ''
            # Look for URLs that might be API endpoints
            urls_in_script = re.findall(r'["\']https?://[^"\']+["\']', script_content)
            for url_match in urls_in_script:
                url = url_match.strip('"\'')
                if 'product' in url.lower() or 'api' in url.lower():
                    if url not in pages_to_check:
                        pages_to_check.append(url)
        
        return list(set(pages_to_check))  # Remove duplicates
    
    def extract_products_from_page(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract products from a single page"""
        products = []
        
        # Multiple approaches to find products
        approaches = [
            self.extract_from_product_containers,
            self.extract_from_structured_data,
            self.extract_from_price_elements,
            self.extract_from_images_with_prices
        ]
        
        for approach in approaches:
            found_products = approach(soup, url)
            if found_products:
                print(f"✅ Found {len(found_products)} products using {approach.__name__}")
                products.extend(found_products)
                break  # Use the first successful approach
        
        return products
    
    def extract_from_product_containers(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract products from typical e-commerce container elements"""
        products = []
        
        # Try different selectors for product containers
        product_selectors = [
            '.product', '.product-item', '.product-card', '.item', '.product-container',
            '[data-product]', '[data-product-id]', '.grid-item', '.shop-item',
            '.catalog-item', '.listing-item', '.merchandise', '.goods'
        ]
        
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"  📦 Trying selector: {selector} (found {len(elements)} elements)")
                
                for element in elements:
                    product = self.extract_product_from_element(element, url)
                    if product and (product.get('name') or product.get('price')):
                        products.append(product)
                
                if products:  # If we found products with this selector, use it
                    break
        
        return products
    
    def extract_from_structured_data(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract products from JSON-LD structured data"""
        products = []
        
        # Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                
                # Handle different structured data formats
                if isinstance(data, list):
                    for item in data:
                        product = self.parse_structured_data_item(item, url)
                        if product:
                            products.append(product)
                elif isinstance(data, dict):
                    product = self.parse_structured_data_item(data, url)
                    if product:
                        products.append(product)
                        
            except json.JSONDecodeError:
                continue
        
        return products
    
    def parse_structured_data_item(self, item: dict, url: str) -> Dict:
        """Parse a single structured data item"""
        if not isinstance(item, dict):
            return None
        
        item_type = item.get('@type', '').lower()
        if 'product' not in item_type:
            return None
        
        product = {
            'name': item.get('name', ''),
            'description': item.get('description', ''),
            'url': url,
            'price': None,
            'original_price': None,
            'image_url': '',
            'brand': item.get('brand', {}).get('name', '') if isinstance(item.get('brand'), dict) else item.get('brand', ''),
            'sku': item.get('sku', ''),
            'availability': item.get('availability', '')
        }
        
        # Extract offers/price information
        offers = item.get('offers', {})
        if isinstance(offers, dict):
            product['price'] = self.clean_price(str(offers.get('price', '')))
        elif isinstance(offers, list) and offers:
            product['price'] = self.clean_price(str(offers[0].get('price', '')))
        
        # Extract image
        image = item.get('image')
        if isinstance(image, list) and image:
            product['image_url'] = image[0]
        elif isinstance(image, str):
            product['image_url'] = image
        
        return product
    
    def extract_from_price_elements(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Find products by looking for price elements and working backwards"""
        products = []
        
        # Find all elements that look like prices
        price_patterns = [
            r'\$\d+(?:\.\d{2})?',  # $123.45
            r'USD\s*\d+(?:\.\d{2})?',  # USD 123.45
            r'\d+(?:\.\d{2})?\s*USD',  # 123.45 USD
            r'€\d+(?:\.\d{2})?',  # €123.45
            r'£\d+(?:\.\d{2})?',  # £123.45
        ]
        
        price_elements = []
        for pattern in price_patterns:
            elements = soup.find_all(string=re.compile(pattern))
            price_elements.extend(elements)
        
        # For each price element, try to find the product container
        for price_text in price_elements[:20]:  # Limit to avoid too many
            price_element = price_text.parent
            if not price_element:
                continue
            
            # Walk up the DOM to find a product container
            current = price_element
            for _ in range(5):  # Don't go too far up
                if current is None:
                    break
                
                # Check if this looks like a product container
                if self.looks_like_product_container(current):
                    product = self.extract_product_from_element(current, url)
                    if product and product not in products:
                        products.append(product)
                    break
                
                current = current.parent
        
        return products
    
    def extract_from_images_with_prices(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Find products by looking for images near price text"""
        products = []
        
        # Find all images
        images = soup.find_all('img')
        
        for img in images:
            # Look for price text near the image
            parent = img.parent
            if not parent:
                continue
            
            # Check siblings and nearby elements for price text
            nearby_text = parent.get_text()
            if re.search(r'\$\d+|\d+\s*USD|€\d+|£\d+', nearby_text):
                product = self.extract_product_from_element(parent, url)
                if product and product not in products:
                    products.append(product)
        
        return products
    
    def looks_like_product_container(self, element) -> bool:
        """Check if an element looks like it contains product information"""
        if not element or not hasattr(element, 'get_text'):
            return False
        
        text = element.get_text().lower()
        class_names = ' '.join(element.get('class', [])).lower()
        
        # Look for product-related keywords
        product_keywords = ['product', 'item', 'goods', 'merchandise', 'catalog']
        has_product_keyword = any(keyword in class_names for keyword in product_keywords)
        
        # Look for price and name indicators
        has_price = bool(re.search(r'\$\d+|\d+\s*usd|€\d+|£\d+', text))
        has_reasonable_length = 10 < len(text) < 500
        
        return has_product_keyword or (has_price and has_reasonable_length)
    
    def extract_product_from_element(self, element, page_url: str) -> Dict:
        """Extract product information from a single element"""
        if not element:
            return None
        
        product = {
            'name': '',
            'price': None,
            'original_price': None,
            'description': '',
            'image_url': '',
            'product_url': page_url,
            'brand': '',
            'sku': '',
            'availability': ''
        }
        
        # Extract name
        name_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.product-title', '.product-name', '[data-title]']
        for selector in name_selectors:
            name_elem = element.select_one(selector)
            if name_elem and name_elem.get_text(strip=True):
                product['name'] = name_elem.get_text(strip=True)
                break
        
        # If no name found in selectors, try to get it from alt text or title attributes
        if not product['name']:
            img = element.select_one('img')
            if img:
                product['name'] = img.get('alt', '') or img.get('title', '')
        
        # Extract price
        element_text = element.get_text()
        price_matches = re.findall(r'\$(\d+(?:\.\d{2})?)|(\d+(?:\.\d{2})?)\s*USD', element_text)
        if price_matches:
            for match in price_matches:
                price_str = match[0] or match[1]
                price = self.clean_price(price_str)
                if price:
                    product['price'] = price
                    break
        
        # Try specific price selectors
        if not product['price']:
            price_selectors = ['.price', '.cost', '.amount', '.money', '[data-price]']
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price = self.clean_price(price_elem.get_text(strip=True))
                    if price:
                        product['price'] = price
                        break
        
        # Extract description (limit length)
        desc_elem = element.select_one('.description, .product-description, .summary, .details')
        if desc_elem:
            desc_text = desc_elem.get_text(strip=True)
            if len(desc_text) > 20:
                product['description'] = desc_text[:300] + '...' if len(desc_text) > 300 else desc_text
        
        # Extract image URL
        img_elem = element.select_one('img')
        if img_elem:
            src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-lazy-src')
            if src:
                product['image_url'] = urljoin(self.base_url, src)
        
        # Extract product URL (if different from page URL)
        link_elem = element.select_one('a')
        if link_elem:
            href = link_elem.get('href')
            if href:
                product['product_url'] = urljoin(self.base_url, href)
        
        return product
    
    def scrape_all_products(self) -> List[Dict]:
        """Main method to scrape all products from the website"""
        print("🚀 Starting comprehensive product scraping...")
        print("-" * 60)
        
        # Discover all pages
        pages = self.find_all_pages()
        print(f"📄 Found {len(pages)} pages to check")
        
        # Scrape each page
        for i, page_url in enumerate(pages, 1):
            print(f"\n📄 Checking page {i}/{len(pages)}: {page_url}")
            
            soup = self.get_page(page_url)
            if soup:
                page_products = self.extract_products_from_page(soup, page_url)
                if page_products:
                    self.products.extend(page_products)
                    print(f"  ✅ Found {len(page_products)} products on this page")
                else:
                    print(f"  ❌ No products found on this page")
            
            # Be respectful - add delay between requests
            time.sleep(1)
        
        # Remove duplicates based on name and price
        unique_products = []
        seen = set()
        for product in self.products:
            key = (product.get('name', '').lower(), product.get('price', 0))
            if key not in seen:
                seen.add(key)
                unique_products.append(product)
        
        self.products = unique_products
        print(f"\n🎉 Scraping completed! Found {len(self.products)} unique products")
        return self.products
    
    def display_results_table(self):
        """Display results in a comprehensive table format"""
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
        
        # Create a comprehensive display
        print("\n" + "="*150)
        print("🛍️  SHOPDYDY.COM COMPREHENSIVE PRODUCT CATALOG")
        print("="*150)
        
        # Display main table
        display_cols = ['name', 'formatted_price', 'description']
        available_cols = [col for col in display_cols if col in df.columns]
        
        if available_cols:
            display_df = df[available_cols].copy()
            
            # Rename columns for better display
            column_names = {
                'name': 'Product Name',
                'formatted_price': 'Price',
                'description': 'Description'
            }
            display_df = display_df.rename(columns=column_names)
            
            # Truncate long descriptions
            if 'Description' in display_df.columns:
                display_df['Description'] = display_df['Description'].apply(
                    lambda x: (x[:80] + '...') if len(str(x)) > 80 else x
                )
            
            print(display_df.to_string(index=False, max_colwidth=80))
        
        print("="*150)
        print(f"📊 SUMMARY STATISTICS")
        print("-" * 50)
        print(f"Total Products Found: {len(self.products)}")
        
        if 'price' in df.columns:
            prices = df['price'].dropna()
            prices = prices[prices > 0]  # Remove zero prices
            
            if len(prices) > 0:
                print(f"Products with Prices: {len(prices)}")
                print(f"Price Range: ${prices.min():.2f} - ${prices.max():.2f}")
                print(f"Average Price: ${prices.mean():.2f}")
                print(f"Median Price: ${prices.median():.2f}")
        
        # Show product sources
        if 'product_url' in df.columns:
            unique_sources = df['product_url'].nunique()
            print(f"Unique Product Sources: {unique_sources}")
        
        print("="*150)
    
    def save_to_csv(self, filename='comprehensive_shopdydy_products.csv'):
        """Save products to CSV"""
        if not self.products:
            print("No products to save")
            return
        
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        print(f"💾 Data saved to {filename}")
    
    def save_to_json(self, filename='comprehensive_shopdydy_products.json'):
        """Save products to JSON"""
        if not self.products:
            print("No products to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to {filename}")

def main():
    print("🛍️  Comprehensive ShopDydy.com Product Scraper")
    print("=" * 60)
    
    scraper = ComprehensiveShopDydyScraper()
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Display results
            scraper.display_results_table()
            
            # Save results
            scraper.save_to_csv()
            scraper.save_to_json()
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"📦 Found {len(products)} products")
            print("📁 Data saved to:")
            print("   - comprehensive_shopdydy_products.csv")
            print("   - comprehensive_shopdydy_products.json")
        else:
            print("\n❌ No products found.")
            print("   This could be due to:")
            print("   • Anti-scraping measures")
            print("   • Different website structure than expected")
            print("   • Network connectivity issues")
            
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    main()