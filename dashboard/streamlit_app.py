"""
streamlit_app.py

Simple Streamlit Dashboard for Retail Receipt Intelligence

Author: Shikhar Chauhan
Project: Retail Receipt Intelligence
"""

import streamlit as st
import requests
from PIL import Image
import io

# ==========================================================
# Configuration
# ==========================================================

API_BASE_URL = "http://localhost:8000"

# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="Retail Receipt Intelligence",
    layout="wide"
)

# ==========================================================
# Helper Functions
# ==========================================================

def upload_receipt(file):
    """Upload receipt to backend API"""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/receipts/upload", files=files)
        
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error uploading receipt: {str(e)}")
        return None


def get_receipts():
    """Get all receipts from backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}/receipts/")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching receipts: {str(e)}")
        return None


def get_analytics():
    """Get analytics from backend API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching analytics: {str(e)}")
        return None


# ==========================================================
# Main Dashboard
# ==========================================================

def main():
    
    # Title
    st.title("Retail Receipt Intelligence")
    st.markdown("---")
    
    # Upload Section
    st.header("Upload Receipt")
    
    uploaded_file = st.file_uploader("Choose Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        
        if st.button("Upload Button"):
            
            with st.spinner("Processing receipt..."):
                
                result = upload_receipt(uploaded_file)
                
                if result and result.get("success"):
                    
                    receipt = result.get("receipt")
                    
                    st.success("Receipt processed successfully!")
                    
                    st.markdown("---")
                    
                    # Display Images
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Uploaded Image")
                        original_image = Image.open(uploaded_file)
                        st.image(original_image, use_container_width=True)
                    
                    with col2:
                        st.subheader("Detected Cropped Receipt")
                        if receipt.get("crop_path"):
                            try:
                                crop_image = Image.open(receipt["crop_path"])
                                st.image(crop_image, use_container_width=True)
                            except:
                                st.warning("Cropped image not available")
                    
                    st.markdown("---")
                    
                    # Extracted Receipt Information
                    st.subheader("Extracted Receipt Information")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Store", receipt.get("store") or "N/A")
                        st.metric("Date", receipt.get("date") or "N/A")
                        st.metric("Time", receipt.get("time") or "N/A")
                    
                    with col2:
                        st.metric("Subtotal", f"${receipt.get('subtotal', 0):.2f}" if receipt.get('subtotal') else "N/A")
                        st.metric("Tax", f"${receipt.get('tax', 0):.2f}" if receipt.get('tax') else "N/A")
                        st.metric("Total", f"${receipt.get('total', 0):.2f}" if receipt.get('total') else "N/A")
                    
                    with col3:
                        st.metric("Payment Method", receipt.get("payment_method") or "N/A")
                        st.metric("Confidence Score", f"{receipt.get('confidence_score', 0):.2f}")
                        st.metric("Confidence Level", receipt.get("confidence_level", "N/A"))
                    
                    st.markdown("---")
                    
                    # Purchased Items Table
                    st.subheader("Purchased Items Table")
                    
                    items = receipt.get("items", [])
                    
                    if items:
                        items_data = []
                        for item in items:
                            items_data.append({
                                "Item Name": item.get("item_name", "N/A"),
                                "Quantity": item.get("quantity", 1),
                                "Price": f"${item.get('price', 0):.2f}"
                            })
                        st.table(items_data)
                    else:
                        st.info("No items extracted")
                    
                    st.markdown("---")
                    
                    # Processing Status
                    st.subheader("Processing Status")
                    
                    status = receipt.get("processing_status", "Unknown")
                    
                    if status == "Processed Successfully":
                        st.success(status)
                    else:
                        st.warning(status)
    
    st.markdown("---")
    
    # Recent Receipts Section
    st.header("Recent Receipts")
    
    receipts_data = get_receipts()
    
    if receipts_data:
        receipts = receipts_data.get("receipts", [])
        
        if receipts:
            recent_data = []
            for receipt in receipts:
                recent_data.append({
                    "Receipt ID": receipt.get("id", "N/A"),
                    "Store": receipt.get("store") or "N/A",
                    "Date": receipt.get("date") or "N/A",
                    "Total": f"${receipt.get('total', 0):.2f}" if receipt.get('total') else "N/A",
                    "Confidence": f"{receipt.get('confidence_score', 0):.2f}"
                })
            st.table(recent_data)
        else:
            st.info("No receipts found")
    
    st.markdown("---")
    
    # Analytics Section
    st.header("Analytics Section")
    
    analytics = get_analytics()
    
    if analytics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Receipts", analytics.get("total_receipts", 0))
        
        with col2:
            st.metric("Average Confidence", f"{analytics.get('average_confidence', 0):.2f}")
        
        with col3:
            st.metric("Needs Review", analytics.get("needs_review", 0))


# ==========================================================
# Run App
# ==========================================================

if __name__ == "__main__":
    main()
