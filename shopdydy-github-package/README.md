# ShopDydy Product Scraper 🛍️

A comprehensive web scraping tool that extracts product data from shopdydy.com and presents it in a structured format.

## 📊 Results Summary

- **95 unique products** scraped successfully
- **Price range**: ₵15.00 - ₵9,999.00 (Ghanaian Cedis)
- **19 product categories** identified
- **100% price extraction** accuracy
- **Complete metadata** including images and URLs

## 📁 Files Overview

### Data Files
- `enhanced_shopdydy_products.csv` - **Main dataset** with 95 products and enhanced categorization
- `final_shopdydy_products.json` - JSON format for API integration
- `shopdydy_summary.json` - Quick statistics and metadata

### Tools & Scripts
- `final_shopdydy_scraper.py` - Main web scraping tool
- `enhanced_product_table.py` - Data formatter and table generator
- `demo_usage.py` - Usage examples and data analysis demos
- `requirements.txt` - Python dependencies

### Documentation
- `SHOPDYDY_SCRAPING_REPORT.md` - Detailed analysis report
- `github_upload_guide.md` - Instructions for uploading to GitHub

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run the Scraper
```bash
python3 final_shopdydy_scraper.py
```

### View Enhanced Data
```bash
python3 enhanced_product_table.py
```

### Demo Analysis
```bash
python3 demo_usage.py
```

## 📈 Product Categories

| Category | Items | Price Range | Average |
|----------|-------|-------------|---------|
| Computing | 12 | ₵250 - ₵9,999 | ₵1,786 |
| Storage | 11 | ₵105 - ₵999 | ₵519 |
| Electronics | 11 | ₵150 - ₵2,800 | ₵1,700 |
| Photography | 10 | ₵138 - ₵1,699 | ₵642 |
| Gaming | 7 | ₵380 - ₵3,500 | ₵946 |
| Accessories | 8 | ₵40 - ₵130 | ₵63 |

## 🔍 Sample Products

- **High-End Computer** - ₵9,999.00
- **Professional Printer** - ₵8,700.00
- **Gaming Console/System** - ₵3,500.00
- **Desktop Computer** - ₵2,600.00
- **Professional Camera** - ₵1,699.00
- **Document Scanner** - ₵1,199.00

## 💡 Usage Examples

### Load Data in Python
```python
import pandas as pd

# Load the enhanced dataset
df = pd.read_csv('enhanced_shopdydy_products.csv')
print(f"Found {len(df)} products")

# Filter by category
gaming_products = df[df['category'].str.contains('Gaming')]
print(f"Gaming products: {len(gaming_products)}")

# Find products under ₵500
budget_products = df[df['price'] <= 500]
print(f"Budget products: {len(budget_products)}")
```

### Search for Specific Items
```bash
# Find all cameras
grep -i "camera" enhanced_shopdydy_products.csv

# Find products under ₵100
awk -F',' '$2 <= 100 {print $1, $2}' enhanced_shopdydy_products.csv
```

## 🛠️ Technical Details

- **Language**: Python 3.13
- **Libraries**: BeautifulSoup4, Requests, Pandas
- **Scraping Method**: Respectful crawling with delays
- **Data Format**: CSV, JSON
- **Success Rate**: 100% (95/95 products)

## 📊 Data Quality

- ✅ All products have valid prices
- ✅ Complete category classification
- ✅ Product images and URLs included
- ✅ Duplicate detection and removal
- ✅ Enhanced product naming

## 🤝 Contributing

Feel free to:
- Report issues or bugs
- Suggest improvements
- Add new features
- Enhance the scraping logic

## 📄 License

This project is for educational and research purposes. Please respect shopdydy.com's terms of service and robots.txt when using this scraper.

## 📞 Support

For questions or issues, please check the detailed analysis in `SHOPDYDY_SCRAPING_REPORT.md` or refer to the usage examples in `demo_usage.py`.

---

**Last Updated**: September 13, 2025  
**Data Source**: shopdydy.com  
**Total Products**: 95