#!/usr/bin/env python3
"""
ShopDydy.com Product Scraper
============================

A comprehensive web scraping agent to collect product data from shopdydy.com
including product names, prices, and other relevant information.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import logging
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import re
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ShopDydyScraper:
    """
    A comprehensive scraper for shopdydy.com that collects product information
    """
    
    def __init__(self, use_selenium=True, headless=True):
        self.base_url = "https://shopdydy.com"
        self.use_selenium = use_selenium
        self.headless = headless
        self.products = []
        self.session = requests.Session()
        self.driver = None
        
        # Set up headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(self.headers)
        
    def setup_selenium(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument(f'--user-agent={self.headers["User-Agent"]}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            return False
    
    def close_driver(self):
        """Close Selenium WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")
    
    def get_page_content(self, url: str, use_selenium: bool = None) -> Optional[BeautifulSoup]:
        """
        Fetch page content using either requests or Selenium
        """
        if use_selenium is None:
            use_selenium = self.use_selenium
            
        try:
            if use_selenium:
                if not self.driver:
                    if not self.setup_selenium():
                        return None
                
                logger.info(f"Fetching page with Selenium: {url}")
                self.driver.get(url)
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Additional wait for dynamic content
                time.sleep(2)
                
                html_content = self.driver.page_source
                return BeautifulSoup(html_content, 'html.parser')
            
            else:
                logger.info(f"Fetching page with requests: {url}")
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
                
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None
    
    def extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numerical price from text
        """
        if not price_text:
            return None
            
        # Remove common currency symbols and whitespace
        price_text = re.sub(r'[^\d.,]', '', price_text.strip())
        
        # Handle different decimal separators
        if ',' in price_text and '.' in price_text:
            # Assume format like "1,234.56"
            price_text = price_text.replace(',', '')
        elif ',' in price_text:
            # Could be "1,56" (European format) or "1,234" (thousands separator)
            if len(price_text.split(',')[-1]) == 2:
                price_text = price_text.replace(',', '.')
            else:
                price_text = price_text.replace(',', '')
        
        try:
            return float(price_text)
        except (ValueError, TypeError):
            return None
    
    def discover_product_pages(self) -> List[str]:
        """
        Discover product catalog pages and individual product URLs
        """
        product_urls = []
        
        # Try common e-commerce URL patterns
        common_paths = [
            '/',
            '/products',
            '/shop',
            '/catalog',
            '/store',
            '/collections',
            '/categories'
        ]
        
        for path in common_paths:
            url = urljoin(self.base_url, path)
            soup = self.get_page_content(url)
            
            if soup:
                # Look for product links
                product_links = self.find_product_links(soup)
                product_urls.extend(product_links)
                logger.info(f"Found {len(product_links)} product links from {url}")
        
        # Remove duplicates
        return list(set(product_urls))
    
    def find_product_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Find product links in a page
        """
        product_links = []
        
        # Common selectors for product links
        selectors = [
            'a[href*="product"]',
            'a[href*="/p/"]',
            'a[href*="/item/"]',
            '.product-link',
            '.product-item a',
            '.product-card a',
            '.product a',
            'a.product',
            '[data-product-id] a',
            '.item-link'
        ]
        
        for selector in selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    product_links.append(full_url)
        
        return product_links
    
    def extract_product_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract product information from a product page
        """
        product = {
            'url': url,
            'name': None,
            'price': None,
            'original_price': None,
            'description': None,
            'availability': None,
            'brand': None,
            'category': None,
            'image_url': None,
            'sku': None
        }
        
        # Extract product name
        name_selectors = [
            'h1',
            '.product-title',
            '.product-name',
            '[data-product-title]',
            '.title',
            '.product h1',
            '.product-info h1',
            'h1.product-title'
        ]
        
        for selector in name_selectors:
            element = soup.select_one(selector)
            if element and element.get_text(strip=True):
                product['name'] = element.get_text(strip=True)
                break
        
        # Extract price
        price_selectors = [
            '.price',
            '.product-price',
            '[data-price]',
            '.current-price',
            '.sale-price',
            '.price-current',
            '.product-price-current',
            '.money',
            '.amount'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                price = self.extract_price(price_text)
                if price:
                    product['price'] = price
                    break
        
        # Extract original price (if on sale)
        original_price_selectors = [
            '.original-price',
            '.regular-price',
            '.was-price',
            '.price-original',
            '.compare-price',
            '.old-price'
        ]
        
        for selector in original_price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                original_price = self.extract_price(price_text)
                if original_price:
                    product['original_price'] = original_price
                    break
        
        # Extract description
        desc_selectors = [
            '.product-description',
            '.description',
            '.product-details',
            '.product-info',
            '[data-product-description]'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                desc_text = element.get_text(strip=True)
                if len(desc_text) > 20:  # Only if substantial content
                    product['description'] = desc_text[:500]  # Limit length
                    break
        
        # Extract image URL
        img_selectors = [
            '.product-image img',
            '.product-photo img',
            '.main-image img',
            'img[data-product-image]',
            '.product img'
        ]
        
        for selector in img_selectors:
            element = soup.select_one(selector)
            if element:
                src = element.get('src') or element.get('data-src')
                if src:
                    product['image_url'] = urljoin(self.base_url, src)
                    break
        
        # Extract availability
        availability_selectors = [
            '.availability',
            '.stock-status',
            '.in-stock',
            '.out-of-stock',
            '[data-availability]'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                product['availability'] = element.get_text(strip=True)
                break
        
        return product
    
    def scrape_products(self, max_products: int = None) -> List[Dict]:
        """
        Main method to scrape all products
        """
        logger.info("Starting product scraping...")
        
        # First, check if the website is accessible
        soup = self.get_page_content(self.base_url)
        if not soup:
            logger.error(f"Unable to access {self.base_url}")
            return []
        
        logger.info(f"Successfully accessed {self.base_url}")
        
        # Discover product URLs
        product_urls = self.discover_product_pages()
        
        if not product_urls:
            logger.warning("No product URLs found, trying to extract from main page")
            # Try to extract products directly from the main page
            products_from_main = self.extract_products_from_listing(soup)
            if products_from_main:
                self.products.extend(products_from_main)
        
        # Limit the number of products if specified
        if max_products and len(product_urls) > max_products:
            product_urls = product_urls[:max_products]
            logger.info(f"Limited to first {max_products} products")
        
        # Scrape individual product pages
        for i, url in enumerate(product_urls, 1):
            logger.info(f"Scraping product {i}/{len(product_urls)}: {url}")
            
            soup = self.get_page_content(url)
            if soup:
                product = self.extract_product_info(soup, url)
                if product['name'] or product['price']:  # Only add if we got useful data
                    self.products.append(product)
                    logger.info(f"Extracted: {product['name']} - ${product['price']}")
            
            # Be respectful - add delay between requests
            time.sleep(1)
        
        logger.info(f"Scraping completed. Found {len(self.products)} products")
        return self.products
    
    def extract_products_from_listing(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract products directly from a listing page
        """
        products = []
        
        # Look for product containers
        product_selectors = [
            '.product-item',
            '.product-card',
            '.product',
            '.item',
            '[data-product-id]',
            '.grid-item'
        ]
        
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                logger.info(f"Found {len(product_elements)} products using selector: {selector}")
                
                for element in product_elements:
                    product = self.extract_product_from_element(element)
                    if product['name'] or product['price']:
                        products.append(product)
                
                break  # Use first successful selector
        
        return products
    
    def extract_product_from_element(self, element) -> Dict:
        """
        Extract product info from a single product element
        """
        product = {
            'name': None,
            'price': None,
            'original_price': None,
            'url': None,
            'image_url': None
        }
        
        # Extract name
        name_element = (
            element.select_one('h1, h2, h3, h4, .title, .name, .product-title, .product-name') or
            element.select_one('a[title]')
        )
        if name_element:
            product['name'] = name_element.get_text(strip=True) or name_element.get('title', '').strip()
        
        # Extract price
        price_element = element.select_one('.price, .cost, .amount, .money, [data-price]')
        if price_element:
            price = self.extract_price(price_element.get_text(strip=True))
            if price:
                product['price'] = price
        
        # Extract URL
        link_element = element.select_one('a')
        if link_element:
            href = link_element.get('href')
            if href:
                product['url'] = urljoin(self.base_url, href)
        
        # Extract image
        img_element = element.select_one('img')
        if img_element:
            src = img_element.get('src') or img_element.get('data-src')
            if src:
                product['image_url'] = urljoin(self.base_url, src)
        
        return product
    
    def save_to_csv(self, filename: str = 'shopdydy_products.csv'):
        """Save products to CSV file"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        df = pd.DataFrame(self.products)
        df.to_csv(filename, index=False)
        logger.info(f"Products saved to {filename}")
    
    def save_to_json(self, filename: str = 'shopdydy_products.json'):
        """Save products to JSON file"""
        if not self.products:
            logger.warning("No products to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.products, f, indent=2, ensure_ascii=False)
        logger.info(f"Products saved to {filename}")
    
    def display_table(self):
        """Display products in a formatted table"""
        if not self.products:
            logger.warning("No products to display")
            return
        
        df = pd.DataFrame(self.products)
        
        # Select key columns for display
        display_columns = ['name', 'price', 'original_price', 'availability', 'url']
        available_columns = [col for col in display_columns if col in df.columns]
        
        if available_columns:
            display_df = df[available_columns]
            print("\n" + "="*100)
            print("SHOPDYDY.COM PRODUCT CATALOG")
            print("="*100)
            print(display_df.to_string(index=False, max_colwidth=50))
            print("="*100)
            print(f"Total Products Found: {len(self.products)}")
        else:
            print("No data available to display")

def main():
    """Main function to run the scraper"""
    print("ShopDydy.com Product Scraper")
    print("="*50)
    
    # Initialize scraper
    scraper = ShopDydyScraper(use_selenium=True, headless=True)
    
    try:
        # Scrape products
        products = scraper.scrape_products(max_products=50)  # Limit for testing
        
        if products:
            # Display results
            scraper.display_table()
            
            # Save results
            scraper.save_to_csv()
            scraper.save_to_json()
            
            print(f"\nScraping completed successfully!")
            print(f"Found {len(products)} products")
            print("Data saved to:")
            print("- shopdydy_products.csv")
            print("- shopdydy_products.json")
        else:
            print("No products found. The website might be using different selectors or have anti-scraping measures.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()