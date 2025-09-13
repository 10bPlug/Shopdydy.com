#!/usr/bin/env python3
"""
Demo Usage of ShopDydy Product Data
===================================

Demonstrates how to use the scraped product data for analysis and insights.
"""

import pandas as pd
import json

def load_and_analyze_data():
    """Load and perform basic analysis on the scraped data"""
    
    print("🛍️  ShopDydy Product Data Analysis Demo")
    print("=" * 50)
    
    try:
        # Load the enhanced product data
        df = pd.read_csv('enhanced_shopdydy_products.csv')
        print(f"✅ Loaded {len(df)} products from enhanced_shopdydy_products.csv")
        
        # Basic statistics
        print(f"\n📊 Quick Stats:")
        print(f"   • Total Products: {len(df)}")
        print(f"   • Price Range: ₵{df['price'].min():.2f} - ₵{df['price'].max():.2f}")
        print(f"   • Average Price: ₵{df['price'].mean():.2f}")
        print(f"   • Categories: {df['category'].nunique()}")
        
        # Most expensive products
        print(f"\n💰 Top 5 Most Expensive Products:")
        top_expensive = df.nlargest(5, 'price')[['name', 'price', 'category']]
        for _, product in top_expensive.iterrows():
            category = product['category'].replace('Electronics > ', '')
            print(f"   • {product['name']} - ₵{product['price']:,.2f} ({category})")
        
        # Best budget options
        print(f"\n💡 Top 5 Budget-Friendly Options:")
        budget_options = df.nsmallest(5, 'price')[['name', 'price', 'category']]
        for _, product in budget_options.iterrows():
            category = product['category'].replace('Electronics > ', '')
            print(f"   • {product['name']} - ₵{product['price']:,.2f} ({category})")
        
        # Category analysis
        print(f"\n📂 Products by Category:")
        category_counts = df['category'].str.replace('Electronics > ', '').value_counts()
        for category, count in category_counts.head(5).items():
            avg_price = df[df['category'].str.contains(category, na=False)]['price'].mean()
            print(f"   • {category}: {count} products (avg: ₵{avg_price:.2f})")
        
        # Price range distribution
        budget = len(df[df['price'] <= 100])
        mid_range = len(df[(df['price'] > 100) & (df['price'] <= 1000)])
        premium = len(df[df['price'] > 1000])
        
        print(f"\n💵 Price Distribution:")
        print(f"   • Budget (≤₵100): {budget} products ({budget/len(df)*100:.1f}%)")
        print(f"   • Mid-Range (₵101-₵1,000): {mid_range} products ({mid_range/len(df)*100:.1f}%)")
        print(f"   • Premium (>₵1,000): {premium} products ({premium/len(df)*100:.1f}%)")
        
        return df
        
    except FileNotFoundError:
        print("❌ Enhanced product data not found. Please run the scraper first:")
        print("   python3 final_shopdydy_scraper.py")
        print("   python3 enhanced_product_table.py")
        return None

def search_products(df, query, max_results=5):
    """Search for products matching a query"""
    if df is None:
        return
    
    print(f"\n🔍 Searching for: '{query}'")
    print("-" * 30)
    
    # Search in product names and categories
    mask = (df['name'].str.contains(query, case=False, na=False) | 
            df['category'].str.contains(query, case=False, na=False))
    
    results = df[mask].head(max_results)
    
    if len(results) == 0:
        print("   No products found matching your search.")
    else:
        for _, product in results.iterrows():
            category = product['category'].replace('Electronics > ', '')
            print(f"   • {product['name']} - ₵{product['price']:,.2f} ({category})")

def find_products_in_budget(df, max_budget):
    """Find products within a specific budget"""
    if df is None:
        return
    
    print(f"\n💰 Products under ₵{max_budget:,.2f}:")
    print("-" * 30)
    
    budget_products = df[df['price'] <= max_budget].sort_values('price')
    
    if len(budget_products) == 0:
        print("   No products found within this budget.")
    else:
        print(f"   Found {len(budget_products)} products:")
        for _, product in budget_products.head(10).iterrows():
            category = product['category'].replace('Electronics > ', '')
            print(f"   • {product['name']} - ₵{product['price']:,.2f} ({category})")
        
        if len(budget_products) > 10:
            print(f"   ... and {len(budget_products) - 10} more products")

def main():
    """Main demo function"""
    
    # Load and analyze data
    df = load_and_analyze_data()
    
    if df is not None:
        # Demo searches
        search_products(df, "camera", 3)
        search_products(df, "gaming", 3)
        search_products(df, "cable", 3)
        
        # Budget searches
        find_products_in_budget(df, 100)
        find_products_in_budget(df, 500)
        
        print(f"\n✅ Demo completed!")
        print(f"📁 Data files available:")
        print(f"   • enhanced_shopdydy_products.csv")
        print(f"   • final_shopdydy_products.json")
        print(f"   • shopdydy_summary.json")
        
        print(f"\n🔧 Usage Examples:")
        print(f"   # Load data in Python:")
        print(f"   import pandas as pd")
        print(f"   df = pd.read_csv('enhanced_shopdydy_products.csv')")
        print(f"   ")
        print(f"   # Find all gaming products:")
        print(f"   gaming = df[df['category'].str.contains('Gaming')]")
        print(f"   ")
        print(f"   # Products under ₵200:")
        print(f"   budget = df[df['price'] <= 200]")

if __name__ == "__main__":
    main()