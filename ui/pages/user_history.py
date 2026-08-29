"""
User Account History Page
Shows QR code for complete battery entry history
"""

import streamlit as st
from pathlib import Path
import sys
from PIL import Image

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import AppConfig
from utils.qr_generator import QRCodeGenerator


def render_user_history():
    """Render user account history QR code page"""
    
    st.title("📋 Full History QR Code")
    st.markdown("Scan this QR code to view your complete battery entry history")
    
    # Get current user wallet
    current_user_wallet = st.session_state.get("user_wallet", "")
    
    if not current_user_wallet:
        st.warning("⚠️ No user wallet found. Please login first.")
        return
    
    # Generate QR code for user history
    st.markdown("---")
    
    try:
        qr_generator = QRCodeGenerator()
        qr_result = qr_generator.generate_user_history_qr(current_user_wallet)
        
        if isinstance(qr_result, dict):
            qr_full_path = qr_result.get("overlay_path")
            qr_url = qr_result.get("qr_url", "")
            decoded_message = qr_result.get("decoded_message", "")
        
        if qr_full_path and Path(qr_full_path).exists():
            qr_image = Image.open(qr_full_path)
            
            # Center the QR code
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(qr_image, caption="Scan to view complete battery history", use_container_width=True)
                
                st.success("✅ QR Code Generated Successfully")
                
                # Display decoded message
                if decoded_message:
                    st.markdown("**📋 QR Code URL:**")
                    st.code(decoded_message, language="text")
                
                # Add button to open in new tab
                if qr_url:
                    st.markdown(f"[🔗 Open Account History in New Tab]({qr_url})")
                
                st.info("📱 This QR code contains your complete battery history. Scan to view all entries with timestamps.")
        else:
            st.warning("⚠️ QR code generation failed")
    except Exception as e:
        st.warning(f"Could not generate QR code: {e}")
