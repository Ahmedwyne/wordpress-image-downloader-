# WordPress Image Downloader

This automation tool allows you to bulk download images from the media section of your WordPress dashboard, saving you the hassle of downloading hundreds of files manually. With a simple and user-friendly interface, you can fetch and save all your WordPress media images to your local machine in just a few clicks.

![Screenshot](https://github.com/user-attachments/assets/e5b307f7-11d7-49ab-bdeb-207ef88f4747)

## Features
- Download all images from your WordPress media library automatically
- Simple and intuitive graphical interface (Tkinter)
- Progress bar and status updates
- Choose your download folder
- Handles duplicate filenames
- Secure password entry
- Works with WordPress REST API (requires valid credentials)

## Requirements
- Python 3.7+
- The following Python packages:
  - requests
  - pillow

You can install the required packages with:
```bash
pip install requests pillow
```

## Usage
1. Clone or download this repository.
2. Run the script:
   ```bash
   python wordpress-auto.py
   ```
3. Enter your WordPress site URL, username, and password.
4. Choose a download folder (optional).
5. Click "Download Images" and wait for the process to complete.

## Notes
- Your WordPress account must have permission to access the media library via the REST API.
- For best results, use an Application Password (WordPress 5.6+) or a user with appropriate privileges.
- The script is polite to your server (adds a small delay between requests).

## Security
- Your credentials are not stored or transmitted anywhere except to your WordPress site.
- For production or sensitive use, consider using environment variables or a secrets manager for credentials.

## License
No License

## Disclaimer
This tool is provided as-is. Use at your own risk. Always ensure you have permission to access and download content from the target WordPress site.
