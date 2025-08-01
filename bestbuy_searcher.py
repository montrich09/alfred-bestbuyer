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
import os
from oxylabs import RealtimeClient

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

class BestBuySearcher:
    def __init__(self, root):
        self.root = root
        self.root.title("Best Buy Searcher")
        self.root.geometry("600x120")  # Larger initial height to show search box
        self.root.configure(bg='#2c2c2c')
        
        # Make window more Alfred-like but keep it functional
        # self.root.overrideredirect(True)  # Commented out to keep window controls
        self.root.attributes('-topmost', True)  # Keep on top
        
        # Add rounded corners effect (if supported)
        try:
            self.root.attributes('-alpha', 0.95)  # Slight transparency
        except:
            pass
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Variables
        self.search_var = tk.StringVar()
        self.products = []
        self.current_images = []  # Keep references to prevent garbage collection
        self.oxylabs_available = bool(os.getenv('OXYLABS_USERNAME') and os.getenv('OXYLABS_PASSWORD'))
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with dark theme (Alfred-like)
        main_frame = tk.Frame(self.root, bg='#2c2c2c')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Search frame (centered like Alfred)
        search_frame = tk.Frame(main_frame, bg='#2c2c2c')
        search_frame.pack(fill=tk.X, pady=(10, 10))
        
        # Search entry with Alfred-like styling
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('SF Pro Display', 16),
            relief=tk.FLAT,
            bd=0,
            bg='#3c3c3c',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#007AFF',
            selectforeground='#ffffff'
        )
        
        # Add placeholder text
        self.search_entry.insert(0, "Type to search Best Buy products...")
        self.search_entry.config(fg='#8E8E93')  # Gray color for placeholder
        
        def on_focus_in(event):
            if self.search_entry.get() == "Type to search Best Buy products...":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(fg='#ffffff')
                
        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Type to search Best Buy products...")
                self.search_entry.config(fg='#8E8E93')
                
        self.search_entry.bind('<FocusIn>', on_focus_in)
        self.search_entry.bind('<FocusOut>', on_focus_out)
        self.search_entry.pack(fill=tk.X, padx=20, pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        self.search_entry.bind('<Return>', self.search_products)
        self.search_entry.focus()
        
        # Add subtle border effect
        search_border = tk.Frame(search_frame, bg='#007AFF', height=2)
        search_border.pack(fill=tk.X, padx=20)
        
        # Add close button
        close_button = tk.Button(
            search_frame,
            text="✕",
            font=('SF Pro Display', 12),
            bg='#FF3B30',
            fg='#ffffff',
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            command=self.root.quit
        )
        close_button.pack(side=tk.RIGHT, padx=(0, 20))
        
        # Results container (initially hidden)
        self.results_container = tk.Frame(main_frame, bg='#2c2c2c')
        
        # Status frame (compact)
        status_frame = tk.Frame(self.results_container, bg='#2c2c2c')
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Oxylabs status (smaller)
        oxylabs_status = "✅" if self.oxylabs_available else "⚠️"
        oxylabs_color = "#34C759" if self.oxylabs_available else "#FF3B30"
        
        oxylabs_label = tk.Label(
            status_frame,
            text=oxylabs_status,
            font=('SF Pro Display', 8),
            bg='#2c2c2c',
            fg=oxylabs_color
        )
        oxylabs_label.pack(side=tk.LEFT, padx=20)
        
        # Results label (compact)
        self.results_label = tk.Label(
            self.results_container,
            text="Type to search...",
            font=('SF Pro Display', 10),
            bg='#2c2c2c',
            fg='#8E8E93'
        )
        self.results_label.pack(pady=5, padx=20)
        
        # Create canvas and scrollbar for results (compact)
        self.canvas = tk.Canvas(self.results_container, bg='#2c2c2c', highlightthickness=0, height=200)
        scrollbar = ttk.Scrollbar(self.results_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2c2c2c')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Configure ttk style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScrollbar", background='#3c3c3c', troughcolor='#2c2c2c', 
                       bordercolor='#2c2c2c', lightcolor='#3c3c3c', darkcolor='#3c3c3c')
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def on_search_change(self, event=None):
        """Handle search input changes - show/hide results dynamically"""
        query = self.search_var.get().strip()
        
        if len(query) >= 2:  # Show results after 2 characters
            # Show results container
            self.results_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            
            # Resize window to accommodate results
            self.root.geometry("600x300")
            
            # Update results label
            self.results_label.config(text="Searching...", fg='#FF9500')
            
            # Clear previous results
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Start search after a short delay (debouncing)
            self.root.after_cancel(getattr(self, '_search_after_id', 'dummy'))
            self._search_after_id = self.root.after(500, lambda: self.search_products())
            
        else:
            # Hide results container
            self.results_container.pack_forget()
            self.results_label.config(text="Type to search...", fg='#8E8E93')
            
            # Resize window back to compact size
            self.root.geometry("600x120")
        
    def search_products(self, event=None):
        query = self.search_var.get().strip()
        if not query:
            return
            
        # Show results container if not already visible
        if not self.results_container.winfo_ismapped():
            self.results_container.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.root.geometry("600x300")
            
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        self.results_label.config(text="Searching...", fg='#FF9500')
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
        """Scrape Best Buy for products under $5,995 using Oxylabs Real-Time Crawler
        Optimized with URL price filter for faster response times"""
        products = []
        
        # Get Oxylabs credentials from environment variables
        username = os.getenv('OXYLABS_USERNAME')
        password = os.getenv('OXYLABS_PASSWORD')
        
        print(f"🔍 Checking credentials: username={'*' * len(username) if username else 'None'}, password={'*' * len(password) if password else 'None'}")
        
        if not username or not password:
            print("⚠️  Oxylabs credentials not found.")
            return []
        
        try:
            # Initialize Oxylabs Real-Time Client
            client = RealtimeClient(username=username, password=password)
            
            # Best Buy search URL with price filter for faster response
            search_url = f"https://www.bestbuy.com/site/searchpage.jsp?st={quote_plus(query)}&qp=price_facet=Price~less+than+$5,995"
            
            print(">>>>> Search URL:", search_url);

            # Configure parsing instructions
            parsing_instructions = {
                "products": {
                    "_fns": [
                        {
                            "_fn": "xpath",
                            "_args": ["//div[contains(@class, 'shop-sku-list-item')]"]
                        }
                    ],
                    "_items": {
                        "name": {
                            "_fns": [
                                {
                                    "_fn": "xpath_one",
                                    "_args": [".//h4[contains(@class, 'sku-title') or contains(@class, 'sku-header')]//text()"]
                                }
                            ]
                        },
                        "price": {
                            "_fns": [
                                {
                                    "_fn": "xpath_one",
                                    "_args": [".//div[contains(@class, 'priceView-customer-price') or contains(@class, 'priceView-layout-large')]//text()"]
                                }
                            ]
                        },
                        "image_url": {
                            "_fns": [
                                {
                                    "_fn": "xpath_one",
                                    "_args": [".//img/@src"]
                                }
                            ]
                        },
                        "product_url": {
                            "_fns": [
                                {
                                    "_fn": "xpath_one",
                                    "_args": [".//a[contains(@class, 'image-link')]/@href"]
                                }
                            ]
                        }
                    }
                }
            }
            
            # Make the request using universal scraper
            response = client.universal.scrape_url(                
                url=search_url,
                render="html",
                source="universal",
                geo_location="United States",
                # user_agent_type="desktop",
                parse=True,
                parsing_instructions=parsing_instructions
            )
            
            print(">>>>> Response: ", response);
            print(">>>>> Response type: ", type(response));
            print(">>>>> Response attributes: ", [attr for attr in dir(response) if not attr.startswith('_')]);
            print(">>>>> Response results: ", response.results if hasattr(response, 'results') else 'No results attribute');
            print(">>>>> Response raw: ", response.raw if hasattr(response, 'raw') else 'No raw attribute');

            # Check if the response was successful
            try:
                # Check if response has results
                if hasattr(response, 'results') and response.results:
                    # Get the response data
                    data = response.results
                    print(">>>>> Data type: ", type(data));
                    print(">>>>> Data length: ", len(data) if isinstance(data, list) else 'Not a list');
                    if isinstance(data, list) and len(data) > 0:
                        print(">>>>> First result: ", data[0]);
                    
                    # Extract products from the response
                    if isinstance(data, list) and len(data) > 0:
                        result = data[0]
                        print(">>>>> Result type: ", type(result));
                        print(">>>>> Result keys: ", list(result.keys()) if isinstance(result, dict) else 'Not a dict');
                        
                        if isinstance(result, dict) and 'content' in result and 'products' in result['content']:
                            raw_products = result['content']['products']
                            print(f">>>>> Found {len(raw_products)} raw products");
                            
                            for raw_product in raw_products[:20]:  # Limit to first 20 results
                                try:
                                    product = self._process_oxylabs_product(raw_product, query)
                                    if product:  # Price already filtered by URL
                                        products.append(product)
                                except Exception as e:
                                    print(f">>>>> Error processing product: {e}");
                                    continue
                        else:
                            print(">>>>> No 'content' or 'products' in result");
                    else:
                        print(">>>>> No results in data or empty results");
                    
                    if not products:
                        print("⚠️  No products found via Oxylabs.")
                        return []
                        
                else:
                    print(f"⚠️  Oxylabs request failed - no results in response")
                    return []
                    
            except Exception as e:
                print(f"⚠️  Error processing response: {e}")
                return []
                
        except Exception as e:
            print(f"⚠️  Oxylabs error: {str(e)}")
            print(f"🔍 Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return []
            
        return products
        
    def _process_oxylabs_product(self, raw_product, query):
        """Process product data from Oxylabs response"""
        try:
            # Extract product information
            name = raw_product.get('name', '').strip()
            if not name:
                name = f"{query} - Product"
            
            price_text = raw_product.get('price', '$0')
            price = self._extract_price(price_text)
            
            image_url = raw_product.get('image_url')
            if image_url and not image_url.startswith('http'):
                image_url = urljoin('https://www.bestbuy.com', image_url)
            
            product_url = raw_product.get('product_url')
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
            

        
    def _display_results(self, products):
        """Display search results in the UI"""
        if not products:
            self.results_label.config(text="No products found. Try a different search term or check your Oxylabs credentials.", fg='#FF3B30')
            return
            
        self.results_label.config(text=f"Found {len(products)} products (under $5,995):", fg='#34C759')
        
        # Create product cards
        for i, product in enumerate(products):
            self._create_product_card(product, i)
            
    def _create_product_card(self, product, index):
        """Create a compact product card widget for dropdown style"""
        # Card frame with dark theme (compact)
        card_frame = tk.Frame(
            self.scrollable_frame,
            bg='#3c3c3c',
            relief=tk.FLAT,
            bd=0
        )
        card_frame.pack(fill=tk.X, padx=5, pady=1)
        
        # Product image (smaller)
        try:
            if product['image_url']:
                response = requests.get(product['image_url'], timeout=5)
                img_data = response.content
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.current_images.append(photo)  # Keep reference
                
                img_label = tk.Label(card_frame, image=photo, bg='#3c3c3c')
                img_label.pack(side=tk.LEFT, padx=10, pady=8)
            else:
                # Placeholder
                img_label = tk.Label(
                    card_frame,
                    text="📱",
                    font=('SF Pro Display', 16),
                    bg='#3c3c3c',
                    fg='#8E8E93'
                )
                img_label.pack(side=tk.LEFT, padx=10, pady=8)
        except:
            # Fallback placeholder
            img_label = tk.Label(
                card_frame,
                text="📱",
                font=('SF Pro Display', 16),
                bg='#3c3c3c',
                fg='#8E8E93'
            )
            img_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Product info frame (compact)
        info_frame = tk.Frame(card_frame, bg='#3c3c3c')
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Product name (truncated)
        name_text = product['name'][:60] + "..." if len(product['name']) > 60 else product['name']
        name_label = tk.Label(
            info_frame,
            text=name_text,
            font=('SF Pro Display', 11, 'bold'),
            bg='#3c3c3c',
            fg='#ffffff',
            justify=tk.LEFT
        )
        name_label.pack(anchor=tk.W, pady=(0, 2))
        
        # Price and button in same row
        price_button_frame = tk.Frame(info_frame, bg='#3c3c3c')
        price_button_frame.pack(fill=tk.X)
        
        # Price
        price_label = tk.Label(
            price_button_frame,
            text=f"${product['price']:,.2f}",
            font=('SF Pro Display', 12, 'bold'),
            bg='#3c3c3c',
            fg='#34C759'
        )
        price_label.pack(side=tk.LEFT)
        
        # View button (compact)
        if product['product_url']:
            view_button = tk.Button(
                price_button_frame,
                text="Open",
                command=lambda url=product['product_url']: self._open_url(url),
                font=('SF Pro Display', 9),
                bg='#007AFF',
                fg='#ffffff',
                relief=tk.FLAT,
                bd=0,
                padx=8,
                pady=2,
                cursor='hand2'
            )
            view_button.pack(side=tk.RIGHT, padx=(10, 0))
            
        # Add hover effect
        def on_enter(e):
            card_frame.configure(bg='#4c4c4c')
            info_frame.configure(bg='#4c4c4c')
            price_button_frame.configure(bg='#4c4c4c')
            if 'img_label' in locals():
                img_label.configure(bg='#4c4c4c')
                
        def on_leave(e):
            card_frame.configure(bg='#3c3c3c')
            info_frame.configure(bg='#3c3c3c')
            price_button_frame.configure(bg='#3c3c3c')
            if 'img_label' in locals():
                img_label.configure(bg='#3c3c3c')
                
        card_frame.bind('<Enter>', on_enter)
        card_frame.bind('<Leave>', on_leave)
        info_frame.bind('<Enter>', on_enter)
        info_frame.bind('<Leave>', on_leave)
            
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

def setup_credentials():
    """Setup Oxylabs credentials interactively"""
    print("🔧 Best Buy Searcher - Oxylabs Setup")
    print("=" * 40)
    print()
    print("To use real Best Buy data, you need Oxylabs credentials.")
    print("If you don't have an account, visit: https://oxylabs.io")
    print()
    
    # Check if .env already exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"⚠️  {env_file} already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    # Get credentials
    print("\n📝 Enter your Oxylabs credentials:")
    username = input("Username (email): ").strip()
    password = input("Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required!")
        return False
    
    # Create .env file
    env_content = f"""# Oxylabs Real-Time Crawler Configuration
# Your Oxylabs username (email)
OXYLABS_USERNAME={username}

# Your Oxylabs password
OXYLABS_PASSWORD={password}

# Optional: Oxylabs endpoint (usually not needed, defaults to production)
# OXYLABS_ENDPOINT=https://realtime.oxylabs.io/v1/queries
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n✅ Credentials saved to {env_file}")
        print("🔍 You can now restart the app to use real Best Buy data!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        return False

def main():
    # Check for command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_credentials()
        return
    
    root = tk.Tk()
    print("Starting Best Buy Searcher...")
    app = BestBuySearcher(root)
    print("App initialized, showing window...")
    
    # Set up keyboard shortcuts
    def on_escape(event):
        root.quit()
    
    def on_f1(event):
        app.search_entry.focus()
    
    root.bind('<Escape>', on_escape)
    root.bind('<F1>', on_f1)
    
    # Center window (Alfred-like positioning)
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)  # Center vertically
    root.geometry(f"+{x}+{y}")
    
    # Ensure window is visible and on top
    root.lift()
    root.focus_force()
    
    # Drag functionality removed to fix input issues
    # The window now has normal controls for better usability
    
    root.mainloop()

if __name__ == "__main__":
    main() 