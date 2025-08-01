# Best Buy Product Searcher

An Alfred-style desktop application built with Python that allows you to search for Best Buy products under $5,995. The app features a modern GUI with product images, prices, and direct links to Best Buy.

## Features

- **Modern GUI Interface**: Clean, responsive design with smooth scrolling
- **Real-time Search**: Search Best Buy products with instant results
- **Product Filtering**: Automatically filters products under $5,995
- **Product Details**: Displays product images, names, and prices
- **Direct Links**: Click to view products directly on Best Buy
- **Keyboard Shortcuts**: 
  - `Enter` - Search for products
  - `F1` - Focus search field
  - `Escape` - Exit application
- **Fallback Mode**: Shows mock data if web scraping is unavailable

## Requirements

- Python 3.7 or higher
- Internet connection for web scraping
- Modern web browser (for opening product links)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python bestbuy_searcher.py
   ```

## Usage

1. **Launch the application** - The search window will appear centered on your screen

2. **Enter a search term** - Type any product category or brand name (e.g., "laptop", "Samsung", "gaming")

3. **Search** - Press `Enter` or click the "Search" button

4. **Browse results** - Scroll through the product cards showing:
   - Product image
   - Product name
   - Price (formatted)
   - "View on Best Buy" button

5. **View products** - Click "View on Best Buy" to open the product page in your default browser

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` | Search for products |
| `F1` | Focus search field |
| `Escape` | Exit application |

## Technical Details

### Architecture
- **GUI Framework**: Tkinter with custom styling
- **Web Scraping**: BeautifulSoup4 for parsing Best Buy search results
- **Image Handling**: Pillow for image processing and display
- **Threading**: Background search to prevent UI freezing

### Features
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Graceful fallback to mock data if scraping fails
- **Memory Management**: Proper image reference handling
- **User Experience**: Loading indicators and status messages

### Web Scraping
The application attempts to scrape Best Buy's search results page. If the scraping fails (due to rate limiting, site changes, or network issues), it falls back to displaying mock product data for demonstration purposes.

## Troubleshooting

### Common Issues

1. **No products found**
   - Check your internet connection
   - Try different search terms
   - The app may be using fallback mode

2. **Images not loading**
   - This is normal if the product doesn't have an image
   - Placeholder images will be shown instead

3. **Search not working**
   - Best Buy may have changed their website structure
   - The app will show mock data as a fallback

### Dependencies Issues

If you encounter import errors:

```bash
# Install missing packages
pip install tkinter requests Pillow beautifulsoup4 lxml

# On some systems, tkinter might need to be installed separately
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS (with Homebrew):
brew install python-tk
```

## Development

### Project Structure
```
alfred-bestbuyer/
├── bestbuy_searcher.py    # Main application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Customization

You can modify the application by:

1. **Changing the price limit**: Edit the `5995` value in the `_scrape_bestbuy` method
2. **Adjusting the UI**: Modify colors, fonts, and layout in the `setup_ui` method
3. **Adding features**: Extend the product information or add new search filters

## License

This project is for educational and personal use. Please respect Best Buy's terms of service when using web scraping functionality.

## Disclaimer

This application is not affiliated with Best Buy. Web scraping may be subject to rate limiting or blocking. The application includes fallback functionality for demonstration purposes. # alfred-bestbuyer
