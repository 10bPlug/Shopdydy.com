#!/usr/bin/env python3
"""
Complete Product Table Display
==============================
Displays all 95 products from ShopDydy.com in a clean table format
"""

import pandas as pd

def display_complete_product_table():
    """Display all products in a clean table format"""
    
    # Load the data
    df = pd.read_csv('enhanced_shopdydy_products.csv')
    
    # Sort by price (descending)
    df_sorted = df.sort_values('price', ascending=False)
    
    # Create clean display table
    display_df = df_sorted[['name', 'price', 'category']].copy()
    
    # Format prices
    display_df['price_formatted'] = display_df['price'].apply(lambda x: f"₵{x:,.2f}")
    
    # Clean category names
    display_df['category_clean'] = display_df['category'].str.replace('Electronics > ', '').str.title()
    
    # Create final display table
    final_table = display_df[['name', 'price_formatted', 'category_clean']].copy()
    final_table.columns = ['Product Name', 'Price (GHS)', 'Category']
    
    print("🛍️  COMPLETE SHOPDYDY.COM PRODUCT CATALOG")
    print("=" * 80)
    print(f"Total Products: {len(df)} | Price Range: ₵{df['price'].min():.2f} - ₵{df['price'].max():,.2f}")
    print("=" * 80)
    
    # Display the table with row numbers
    for i, (_, row) in enumerate(final_table.iterrows(), 1):
        print(f"{i:2d}. {row['Product Name']:<35} {row['Price (GHS)']:>12} | {row['Category']}")
    
    print("=" * 80)
    
    # Summary by category
    print("\nCATEGORY SUMMARY:")
    print("-" * 40)
    category_summary = df.groupby('category').agg({
        'price': ['count', 'min', 'max', 'mean']
    }).round(2)
    
    category_summary.columns = ['Count', 'Min Price', 'Max Price', 'Avg Price']
    category_summary = category_summary.sort_values('Count', ascending=False)
    
    for category, row in category_summary.iterrows():
        clean_category = category.replace('Electronics > ', '')
        print(f"{clean_category:<25} | {int(row['Count']):2d} items | ₵{row['Min Price']:>7.2f} - ₵{row['Max Price']:>7.2f} (avg: ₵{row['Avg Price']:>7.2f})")

if __name__ == "__main__":
    display_complete_product_table()