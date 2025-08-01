# Best Buy Product Searcher

An Alfred-style desktop application built with Python that allows you to search for Best Buy products under $5,995. The app features a modern GUI with product images, prices, and direct links to Best Buy.

## Features

- **Compact Alfred-like Interface**: Dark theme with dropdown results that expand as you type
- **Real-time Search**: Search Best Buy products with instant results
- **Optimized Filtering**: URL-level price filtering for faster response times
- **Product Filtering**: Automatically filters products under $5,995
- **Product Details**: Displays product images, names, and prices
- **Direct Links**: Click to view products directly on Best Buy
- **Keyboard Shortcuts**: 
  - `Enter` - Search for products
  - `F1` - Focus search field
  - `Escape` - Exit application
- **Clean Results**: No mock data - shows only real search results

## Requirements

- Python 3.7 or higher
- Internet connection for web scraping
- Modern web browser (for opening product links)
- Oxylabs account (optional, for enhanced data fetching)

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Oxylabs**:
   Create a `.env` file in the project root with your Oxylabs credentials:
   ```bash
   # Oxylabs Real-Time Crawler Configuration
   OXYLABS_USERNAME=your_username@example.com
   OXYLABS_PASSWORD=your_password
   ```

4. **Run the application**:
   ```bash
   python bestbuy_searcher.py
   ```

## Usage

1. **Launch the application** - A compact search box will appear centered on your screen

2. **Start typing** - Results appear as a dropdown list as you type (after 2 characters)

3. **Browse results** - Scroll through the product cards showing:
   - Product image
   - Product name
   - Price (formatted)
   - "Open in Browser" button

4. **View products** - Click "Open in Browser" to open the product page in your default browser

5. **Keyboard shortcuts**:
   - `Escape` - Close the application
   - `F1` - Focus search field
   - `Enter` - Perform search
   - Click the red "✕" button to close

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

### Data Fetching
The application uses Oxylabs Real-Time Crawler for reliable data fetching from Best Buy. This provides:
- **Reliable Access**: Bypasses anti-bot measures
- **Structured Data**: Pre-parsed product information
- **High Success Rate**: Professional proxy infrastructure
- **Optimized Performance**: URL-level price filtering for faster response times
- **Clean Results**: No mock data - shows only real search results

The search is optimized by including price filters directly in the URL (`&qp=price_facet=Price~less+than+$5,995`) to reduce response time and data transfer.

If Oxylabs credentials are not provided or no products are found, the app will display an appropriate message.

## Troubleshooting

### Common Issues

1. **No products found**
   - Check your internet connection
   - Try different search terms
   - Verify your Oxylabs credentials are configured

2. **Images not loading**
   - This is normal if the product doesn't have an image
   - Placeholder images will be shown instead

3. **Search not working**
   - Best Buy may have changed their website structure
   - Check your Oxylabs credentials and account status

### Dependencies Issues

If you encounter import errors:

```bash
# Install missing packages
pip install tkinter requests Pillow beautifulsoup4 lxml oxylabs python-dotenv

# On some systems, tkinter might need to be installed separately
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS (with Homebrew):
brew install python-tk
```

### Oxylabs Setup

To use Oxylabs Real-Time Crawler:

1. **Sign up for Oxylabs**: Visit [oxylabs.io](https://oxylabs.io) and create an account
2. **Get credentials**: Find your username and password in your Oxylabs dashboard
3. **Configure environment**: Copy `oxylabs_config.example` to `.env` and add your credentials
4. **Test connection**: The app will automatically use Oxylabs when credentials are provided

Without Oxylabs credentials, the app will use fallback mock data.

## Development

### Project Structure
```
alfred-bestbuyer/
├── bestbuy_searcher.py    # Main application (everything included)
├── requirements.txt       # Python dependencies
├── .env                  # Oxylabs credentials (create manually)
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

This application is not affiliated with Best Buy. Web scraping may be subject to rate limiting or blocking. The application includes fallback functionality for demonstration purposes. 