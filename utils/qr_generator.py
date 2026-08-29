"""
QR Code Generator for EV Battery Passport
Generates QR codes for battery identification and tracking
"""

import qrcode
import os
from pathlib import Path
from datetime import datetime
import json
import sys

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import AppConfig
    config = AppConfig()
    DEFAULT_SERVER_URL = config.QR_SERVER_URL
except:
    DEFAULT_SERVER_URL = "http://localhost:8000"


class QRCodeGenerator:
    """Generate and manage QR codes for battery passports"""
    
    def __init__(self, qr_code_dir="data/processed/qr_codes"):
        self.qr_code_dir = Path(qr_code_dir)
        self.qr_code_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_battery_qr(self, battery_data, server_url=None):
        """
        Generate QR code for a battery passport with URL to web page
        Args:
            battery_data: Dictionary containing battery information
            server_url: Base URL for the web server (uses config default if not provided)
        Returns:
            Dictionary with QR code file path and metadata
        """
        if server_url is None:
            server_url = DEFAULT_SERVER_URL
            
        passport_id = battery_data.get("passport_id", "UNKNOWN")
        
        # Create QR code data as URL to web page
        qr_url = f"{server_url}/battery/{passport_id}"
        
        # Generate QR code with URL
        qr = qrcode.QRCode(
            version=5,  # Moderate version for URL
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create QR code image with custom colors
        qr_img = qr.make_image(fill_color="#1E3A8A", back_color="#F0F9FF")  # Blue on light blue
        
        # Save QR code
        qr_filename = f"{passport_id}.png"
        qr_path = self.qr_code_dir / qr_filename
        qr_img.save(qr_path)
        
        # Generate metadata
        metadata = {
            "qr_code_path": str(qr_path),
            "qr_code_filename": qr_filename,
            "generated_at": datetime.now().isoformat(),
            "qr_url": qr_url,
            "qr_data": battery_data,  # Store full data for reference
            "file_size": os.path.getsize(qr_path)
        }
        
        return metadata
    
    def get_qr_code_path(self, passport_id):
        """Get the QR code file path for a given passport ID"""
        qr_path = self.qr_code_dir / f"{passport_id}.png"
        return str(qr_path) if qr_path.exists() else None
    
    def generate_batch_qr_codes(self, battery_list):
        """
        Generate QR codes for multiple batteries
        Args:
            battery_list: List of battery data dictionaries
        Returns:
            List of QR code metadata dictionaries
        """
        results = []
        for battery in battery_list:
            try:
                qr_metadata = self.generate_battery_qr(battery)
                results.append({
                    "passport_id": battery.get("passport_id"),
                    "status": "success",
                    **qr_metadata
                })
            except Exception as e:
                results.append({
                    "passport_id": battery.get("passport_id"),
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def create_qr_with_overlay(self, battery_data, label_text="EV BATTERY PASSPORT"):
        """
        Create QR code with simple header only (no battery information text)
        Args:
            battery_data: Battery information
            label_text: Text to display as header
        Returns:
            Dictionary with paths and decoded message
        """
        from PIL import Image, ImageDraw, ImageFont
        
        passport_id = battery_data.get("passport_id", "UNKNOWN")
        
        # Generate basic QR code
        qr_metadata = self.generate_battery_qr(battery_data)
        qr_img = Image.open(qr_metadata["qr_code_path"])
        qr_url = qr_metadata.get("qr_url", "")
        
        # Create larger canvas for QR + simple header only
        img_width, img_height = qr_img.size
        new_height = img_height + 60  # Space for header only
        new_img = Image.new('RGB', (img_width, new_height), '#F0F9FF')  # Light blue background
        
        # Paste QR code
        new_img.paste(qr_img, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(new_img)
        
        # Try to use fonts, fallback to default if not available
        try:
            title_font = ImageFont.truetype("arial.ttf", 20, "bold")
            text_font = ImageFont.truetype("arial.ttf", 12)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Draw header
        draw.text((10, img_height + 10), label_text, fill='#1E3A8A', font=title_font)
        
        # Draw passport ID
        id_text = f"ID: {passport_id[-12:]}"  # Show last 12 chars
        draw.text((10, img_height + 35), id_text, fill='#666666', font=text_font)
        
        # Draw border
        draw.rectangle([(5, 5), (img_width - 5, new_height - 5)], outline='#1E3A8A', width=2)
        
        # Save the combined image
        overlay_path = self.qr_code_dir / f"{passport_id}_full.png"
        new_img.save(overlay_path)
        
        return {
            "overlay_path": str(overlay_path),
            "qr_url": qr_url,
            "decoded_message": qr_url,
            "battery_data": battery_data
        }
    
    def generate_user_history_qr(self, user_wallet, server_url=None):
        """
        Generate QR code for user account history
        Args:
            user_wallet: User wallet address
            server_url: Base URL for the web server (uses config default if not provided)
        Returns:
            Dictionary with QR code file path and metadata
        """
        if server_url is None:
            server_url = DEFAULT_SERVER_URL
        
        # Create QR code data as URL to user history page
        qr_url = f"{server_url}/user/{user_wallet}"
        
        # Generate QR code with URL - most basic approach
        qr = qrcode.QRCode()
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        # Create QR code image with default colors
        qr_img = qr.make_image()
        
        # Save QR code directly
        qr_filename = f"user_{user_wallet[-12:]}.png"
        qr_path = self.qr_code_dir / qr_filename
        qr_img.save(qr_path)
        
        return {
            "overlay_path": str(qr_path),
            "qr_url": qr_url,
            "decoded_message": qr_url,
            "user_wallet": user_wallet
        }
