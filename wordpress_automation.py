import requests
import os
import json
from urllib.parse import urlparse
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import sys

class WordPressImageDownloader:
    def __init__(self, site_url, username, password, download_folder="wordpress_images"):
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2/media"
        self.auth = (username, password)
        self.download_folder = download_folder
        self.downloaded_count = 0
        
        # Create download folder if it doesn't exist
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def fetch_image_urls(self, per_page=130, progress_callback=None):
        """Fetch all image URLs from WordPress media library"""
        image_urls = []
        page = 1
        total_images = 0
        
        # First, get the total number of images
        initial_params = {
            'per_page': 1,
            'page': 1,
            'media_type': 'image'
        }
        
        initial_response = requests.get(self.api_url, params=initial_params, auth=self.auth)
        if initial_response.status_code == 200:
            total_images = int(initial_response.headers.get('X-WP-Total', 0))
        
        if progress_callback:
            progress_callback(0, total_images, "Connecting to WordPress...")
        
        while True:
            params = {
                'per_page': per_page,
                'page': page,
                'media_type': 'image'
            }
            
            try:
                response = requests.get(self.api_url, params=params, auth=self.auth, timeout=30)
                
                if response.status_code != 200:
                    print(f"Error: Received status code {response.status_code}")
                    print(f"Response: {response.text}")
                    break
                
                media_items = response.json()
                
                if not media_items:
                    break
                
                for item in media_items:
                    if 'source_url' in item:
                        image_urls.append(item['source_url'])
                
                if progress_callback:
                    progress_callback(len(image_urls), total_images, f"Fetched {len(image_urls)} image URLs...")
                
                # Check if we've reached the last page
                if len(media_items) < per_page:
                    break
                    
                page += 1
                # Be respectful to the server
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)}")
                break
        
        return image_urls
    
    def download_image(self, url, progress_callback=None):
        """Download a single image from URL"""
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                # Extract filename from URL
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                # Save image to download folder
                filepath = os.path.join(self.download_folder, filename)
                
                # Handle duplicate filenames
                counter = 1
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(filename)
                    filepath = os.path.join(self.download_folder, f"{name}_{counter}{ext}")
                    counter += 1
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                
                self.downloaded_count += 1
                if progress_callback:
                    # Pass current, total, message (total is not tracked here, so pass 0)
                    progress_callback(self.downloaded_count, 0, f"Downloaded {filename}")
                return True
            else:
                print(f"Failed to download {url}: Status code {response.status_code}")
                return False
        except Exception as e:
            print(f"Error downloading {url}: {str(e)}")
            return False
    
    def download_all_images(self, progress_callback=None):
        """Download all images from WordPress media library"""
        if progress_callback:
            progress_callback(0, 0, "Fetching image URLs from WordPress...")
        
        image_urls = self.fetch_image_urls(progress_callback=progress_callback)
        
        if not image_urls:
            if progress_callback:
                progress_callback(0, 0, "No images found or unable to access the WordPress site.")
            return False
        
        if progress_callback:
            progress_callback(0, len(image_urls), f"Starting download of {len(image_urls)} images...")
        
        for i, url in enumerate(image_urls):
            self.download_image(url, progress_callback=progress_callback)
            # Be respectful to the server
            time.sleep(0.1)
        
        if progress_callback:
            progress_callback(len(image_urls), len(image_urls), 
                             f"Download completed. {self.downloaded_count} images downloaded to '{self.download_folder}'.")
        return True


class DownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WordPress Image Downloader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set application icon (if available)
        try:
            self.root.iconbitmap(default="wordpress_icon.ico")
        except:
            pass
        
        # Style configuration
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("Header.TLabel", font=("Arial", 16, "bold"))
        style.configure("Progress.TLabel", font=("Arial", 9))
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(main_frame, text="WordPress Image Downloader", style="Header.TLabel")
        header_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Site URL
        ttk.Label(form_frame, text="WordPress Site URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.site_url = ttk.Entry(form_frame, width=50)
        self.site_url.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Username
        ttk.Label(form_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username = ttk.Entry(form_frame, width=50)
        self.username.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password = ttk.Entry(form_frame, width=50, show="*")
        self.password.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Download folder
        ttk.Label(form_frame, text="Download Folder:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.folder_path = tk.StringVar(value="wordpress_images")
        folder_frame = ttk.Frame(form_frame)
        folder_frame.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=45).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Progress area
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to download images", style="Progress.TLabel")
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="", style="Progress.TLabel")
        self.status_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.download_btn = ttk.Button(button_frame, text="Download Images", command=self.start_download)
        self.download_btn.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=root.quit).pack(side=tk.RIGHT)
        
        # Configure main frame weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Set focus to site URL field
        self.site_url.focus()
        
        # Downloader instance
        self.downloader = None
        self.download_thread = None
        
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Download Folder")
        if folder:
            self.folder_path.set(folder)
    
    def update_progress(self, current, total, message):
        if total > 0:
            self.progress['maximum'] = total
            self.progress['value'] = current
            self.status_label['text'] = f"{current}/{total}"
        self.progress_label['text'] = message
        self.root.update_idletasks()
    
    def download_threaded(self):
        try:
            self.downloader = WordPressImageDownloader(
                self.site_url.get(),
                self.username.get(),
                self.password.get(),
                self.folder_path.get()
            )
            
            success = self.downloader.download_all_images(progress_callback=self.update_progress)
            
            if success:
                messagebox.showinfo("Success", f"Download completed!\n{self.downloader.downloaded_count} images downloaded to\n{self.folder_path.get()}")
            else:
                messagebox.showerror("Error", "Failed to download images. Please check your credentials and try again.")
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            self.download_btn['state'] = 'normal'
    
    def start_download(self):
        if not self.site_url.get() or not self.username.get() or not self.password.get():
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        self.download_btn['state'] = 'disabled'
        self.update_progress(0, 100, "Starting download...")
        
        # Run download in a separate thread to keep UI responsive
        self.download_thread = threading.Thread(target=self.download_threaded)
        self.download_thread.daemon = True
        self.download_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = DownloaderApp(root)
    root.mainloop()
