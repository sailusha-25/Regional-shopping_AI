import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import sys
import hashlib

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the services directly
try:
    from src.services.tavily_shopping_search import TavilyShoppingService
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services"""
    try:
        tavily_service = TavilyShoppingService()
        return tavily_service
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None

# Page configuration
st.set_page_config(
    page_title="Regional Shopping AI",
    page_icon="🛒",
    layout="wide"
)

# Custom CSS for cleaner UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .price-tag {
        background: #4CAF50;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .buy-button {
        background: #ff6b35;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
    }
    
    .list-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛒 Regional Shopping AI</h1>
        <p>Smart online shopping with real-time product search</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize services
    tavily_service = init_services()
    if not tavily_service:
        st.error("Failed to initialize shopping service")
        return
    
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Search Products", "📝 Shopping List"])
    
    with tab1:
        show_product_search(tavily_service)
    
    with tab2:
        show_shopping_list()

def show_product_search(tavily_service):
    """Display the product search interface"""
    st.header("🔍 Search Products Online")
    
    # Search input
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input(
            "",
            placeholder="Search for products (e.g., organic vegetables, fresh milk, electronics)",
            label_visibility="collapsed"
        )
    with col2:
        limit = st.selectbox("Results", [5, 10, 15, 20], index=1)
    
    if search_query:
        with st.spinner("🔍 Searching online stores..."):
            try:
                products = tavily_service.search_products(search_query, limit)
                
                if products:
                    st.success(f"Found {len(products)} products")
                    
                    # Display products in a clean grid
                    for i, product in enumerate(products):
                        with st.container():
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{product.get('title', 'Product')[:80]}**")
                                description = product.get('description', 'No description available')
                                if len(description) > 120:
                                    description = description[:120] + "..."
                                st.write(description)
                                
                                # Source info
                                source = product.get('source', 'Unknown Store')
                                st.caption(f"📍 {source}")
                            
                            with col2:
                                price = product.get('price', 'Price not available')
                                st.markdown(f'<div class="price-tag">{price}</div>', unsafe_allow_html=True)
                                
                                # Relevance score
                                score = product.get('score', 0)
                                st.caption(f"⭐ {score:.1f}/10")
                            
                            with col3:
                                # Buy button
                                if product.get('url'):
                                    st.link_button("🛒 Buy Now", product['url'], use_container_width=True)
                                
                                # Add to list button
                                if st.button("➕ Add to List", key=f"add_{i}", use_container_width=True):
                                    add_to_shopping_list(product)
                                    st.success("Added to list!")
                                    time.sleep(0.5)
                                    st.rerun()
                            
                            st.divider()
                else:
                    st.warning("No products found. Try different keywords.")
                    
            except Exception as e:
                st.error(f"Search error: {e}")

def show_shopping_list():
    """Display the shopping list interface"""
    st.header("📝 Your Shopping List")
    
    if st.session_state.shopping_list:
        # List controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{len(st.session_state.shopping_list)} items** in your list")
        with col2:
            if st.button("📤 Export List"):
                export_shopping_list()
        with col3:
            if st.button("🗑️ Clear All"):
                st.session_state.shopping_list = []
                st.success("List cleared!")
                st.rerun()
        
        st.divider()
        
        # Display list items
        for i, item in enumerate(st.session_state.shopping_list):
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{item['title'][:60]}**")
                    st.caption(f"📍 {item['source']}")
                
                with col2:
                    st.markdown(f'<div class="price-tag">{item["price"]}</div>', unsafe_allow_html=True)
                
                with col3:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if item.get('url'):
                            st.link_button("🛒", item['url'], help="Buy Now")
                    with col_b:
                        if st.button("🗑️", key=f"remove_{i}", help="Remove"):
                            st.session_state.shopping_list.pop(i)
                            st.rerun()
                
                st.divider()
    else:
        st.info("Your shopping list is empty. Search for products to add items!")
        
        # Quick search suggestions
        st.subheader("💡 Quick Search Ideas")
        suggestions = [
            "Fresh vegetables", "Organic milk", "Smartphone", 
            "Laptop", "Books", "Kitchen appliances"
        ]
        
        cols = st.columns(3)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    # Switch to search tab with suggestion
                    st.session_state.search_query = suggestion
                    st.switch_page("streamlit_app.py")

def add_to_shopping_list(product):
    """Add product to shopping list"""
    # Check if already in list
    for item in st.session_state.shopping_list:
        if item.get('url') == product.get('url'):
            return  # Already in list
    
    # Add to list
    list_item = {
        'title': product.get('title', 'Product'),
        'price': product.get('price', 'N/A'),
        'url': product.get('url', ''),
        'source': product.get('source', 'Unknown'),
        'added_at': datetime.now().isoformat()
    }
    
    st.session_state.shopping_list.append(list_item)

def export_shopping_list():
    """Export shopping list as text"""
    if not st.session_state.shopping_list:
        st.warning("No items to export")
        return
    
    # Create export text
    export_text = "🛒 My Shopping List\n"
    export_text += "=" * 30 + "\n\n"
    
    for i, item in enumerate(st.session_state.shopping_list, 1):
        export_text += f"{i}. {item['title']}\n"
        export_text += f"   💰 Price: {item['price']}\n"
        export_text += f"   🏪 Store: {item['source']}\n"
        if item.get('url'):
            export_text += f"   🔗 Link: {item['url']}\n"
        export_text += "\n"
    
    export_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Download button
    st.download_button(
        label="📥 Download Shopping List",
        data=export_text,
        file_name=f"shopping_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main()