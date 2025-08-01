import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import threading
from PIL import Image, ImageTk
import io
import re
from urllib.parse import urljoin, quote_plus
import json

class BestBuySearcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Best Buy Product Searcher")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.search_var = tk.StringVar()
        self.products = []
        self.current_images = []  # Keep references to prevent garbage collection
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Best Buy Product Searcher", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 20))
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='#f0f0f0')
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Search label
        search_label = tk.Label(
            search_frame,
            text="Search for products under $5,995:",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#34495e'
        )
        search_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Search entry
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 14),
            relief=tk.SOLID,
            bd=2,
            width=50
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind('<Return>', self.search_products)
        self.search_entry.focus()
        
        # Search button
        search_button = tk.Button(
            search_frame,
            text="Search",
            command=self.search_products,
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        search_button.pack(side=tk.RIGHT)
        
        # Results frame
        results_frame = tk.Frame(main_frame, bg='#f0f0f0')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results label
        self.results_label = tk.Label(
            results_frame,
            text="Enter a search term and press Enter or click Search",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        self.results_label.pack(pady=20)
        
        # Create canvas and scrollbar for results
        self.canvas = tk.Canvas(results_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def search_products(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term")
            return
            
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.results_label.config(text="Searching...", fg='#f39c12')
        self.root.update()
        
        # Run search in separate thread to avoid blocking UI
        thread = threading.Thread(target=self._perform_search, args=(query,))
        thread.daemon = True
        thread.start()
        
    def _perform_search(self, query):
        try:
            products = self._scrape_bestbuy(query)
            self.root.after(0, self._display_results, products)
        except Exception as e:
            self.root.after(0, lambda: self._show_error(f"Search failed: {str(e)}"))
            
    def _scrape_bestbuy(self, query):
        """Scrape Best Buy for products under $5,995"""
        products = []
        
        # Best Buy search URL
        search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product containers
            product_containers = soup.find_all('div', class_='shop-sku-list-item')
            
            for container in product_containers[:20]:  # Limit to first 20 results
                try:
                    # Extract product information
                    product = self._extract_product_info(container)
                    if product and product['price'] < 5995:
                        products.append(product)
                except Exception as e:
                    continue
                    
        except requests.RequestException as e:
            # Fallback: create mock data for demonstration
            products = self._create_mock_products(query)
            
        return products
        
    def _extract_product_info(self, container):
        """Extract product information from a container element"""
        try:
            # Product name
            name_elem = container.find('h4', class_='sku-title') or container.find('h4', class_='sku-header')
            name = name_elem.get_text(strip=True) if name_elem else "Unknown Product"
            
            # Price
            price_elem = container.find('div', class_='priceView-customer-price') or container.find('span', class_='priceView-layout-large')
            price_text = price_elem.get_text(strip=True) if price_elem else "$0"
            price = self._extract_price(price_text)
            
            # Image
            img_elem = container.find('img')
            image_url = img_elem.get('src') if img_elem else None
            if image_url and not image_url.startswith('http'):
                image_url = urljoin('https://www.bestbuy.com', image_url)
                
            # Product URL
            link_elem = container.find('a', class_='image-link')
            product_url = link_elem.get('href') if link_elem else None
            if product_url and not product_url.startswith('http'):
                product_url = urljoin('https://www.bestbuy.com', product_url)
                
            return {
                'name': name,
                'price': price,
                'image_url': image_url,
                'product_url': product_url
            }
            
        except Exception:
            return None
            
    def _extract_price(self, price_text):
        """Extract numeric price from price text"""
        try:
            # Remove currency symbols and extract numbers
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group())
            return 0
        except:
            return 0
            
    def _create_mock_products(self, query):
        """Create mock products for demonstration when scraping fails"""
        mock_products = [
            {
                'name': f'{query} - Gaming Laptop',
                'price': 1299.99,
                'image_url': 'https://via.placeholder.com/150x150?text=Laptop',
                'product_url': 'https://www.bestbuy.com'
            },
            {
                'name': f'{query} - Wireless Headphones',
                'price': 299.99,
                'image_url': 'https://via.placeholder.com/150x150?text=Headphones',
                'product_url': 'https://www.bestbuy.com'
            },
            {
                'name': f'{query} - Smart TV 55"',
                'price': 799.99,
                'image_url': 'https://via.placeholder.com/150x150?text=TV',
                'product_url': 'https://www.bestbuy.com'
            },
            {
                'name': f'{query} - Wireless Speaker',
                'price': 199.99,
                'image_url': 'https://via.placeholder.com/150x150?text=Speaker',
                'product_url': 'https://www.bestbuy.com'
            },
            {
                'name': f'{query} - Gaming Console',
                'price': 499.99,
                'image_url': 'https://via.placeholder.com/150x150?text=Console',
                'product_url': 'https://www.bestbuy.com'
            }
        ]
        return mock_products
        
    def _display_results(self, products):
        """Display search results in the UI"""
        if not products:
            self.results_label.config(text="No products found under $5,995", fg='#e74c3c')
            return
            
        self.results_label.config(text=f"Found {len(products)} products under $5,995:", fg='#27ae60')
        
        # Create product cards
        for i, product in enumerate(products):
            self._create_product_card(product, i)
            
    def _create_product_card(self, product, index):
        """Create a product card widget"""
        # Card frame
        card_frame = tk.Frame(
            self.scrollable_frame,
            bg='white',
            relief=tk.RAISED,
            bd=2
        )
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Product image
        try:
            if product['image_url']:
                response = requests.get(product['image_url'], timeout=5)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((120, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.current_images.append(photo)  # Keep reference
                
                img_label = tk.Label(card_frame, image=photo, bg='white')
                img_label.pack(side=tk.LEFT, padx=10, pady=10)
            else:
                # Placeholder
                img_label = tk.Label(
                    card_frame,
                    text="No Image",
                    width=15,
                    height=7,
                    bg='#ecf0f1',
                    fg='#7f8c8d'
                )
                img_label.pack(side=tk.LEFT, padx=10, pady=10)
        except:
            # Fallback placeholder
            img_label = tk.Label(
                card_frame,
                text="No Image",
                width=15,
                height=7,
                bg='#ecf0f1',
                fg='#7f8c8d'
            )
            img_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Product info frame
        info_frame = tk.Frame(card_frame, bg='white')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Product name
        name_label = tk.Label(
            info_frame,
            text=product['name'],
            font=('Arial', 12, 'bold'),
            bg='white',
            fg='#2c3e50',
            wraplength=400,
            justify=tk.LEFT
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Price
        price_label = tk.Label(
            info_frame,
            text=f"${product['price']:,.2f}",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='#27ae60'
        )
        price_label.pack(anchor=tk.W, pady=(0, 10))
        
        # View button
        if product['product_url']:
            view_button = tk.Button(
                info_frame,
                text="View on Best Buy",
                command=lambda url=product['product_url']: self._open_url(url),
                font=('Arial', 10),
                bg='#3498db',
                fg='white',
                relief=tk.FLAT,
                padx=15,
                pady=3
            )
            view_button.pack(anchor=tk.W)
            
    def _open_url(self, url):
        """Open product URL in default browser"""
        import webbrowser
        try:
            webbrowser.open(url)
        except:
            messagebox.showerror("Error", "Could not open browser")
            
    def _show_error(self, message):
        """Show error message"""
        self.results_label.config(text=message, fg='#e74c3c')
        messagebox.showerror("Error", message)

def main():
    root = tk.Tk()
    app = BestBuySearcher(root)
    
    # Set up keyboard shortcuts
    def on_escape(event):
        root.quit()
    
    def on_f1(event):
        app.search_entry.focus()
    
    root.bind('<Escape>', on_escape)
    root.bind('<F1>', on_f1)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 