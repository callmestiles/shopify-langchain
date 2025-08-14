import shopify
from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

# Configure shopify API
def setup_shopify_session(shop_url: str, access_token: str):
    """Initialize Shopify session"""
    shopify.ShopifyResource.set_site(f"https://{shop_url}.myshopify.com/admin/api/2023-10")
    shopify.ShopifyResource.headers["X-Shopify-Access-Token"] = access_token
 
@tool
def get_products(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve products from Shopify store.
    
    Args:
        limit: Maximum number of products to retrieve (default: 10)
    
    Returns:
        List of product dictionaries with id, title, handle, and status
    """
    try:
        products = shopify.Product.find(limit=limit)
        return [{
                "id": product.id, 
                 "title": product.title, 
                 "handle": product.handle, 
                 "status": product.status, 
                 "vendor": product.vendor, 
                 "product_type": product.product_type, 
                 "created_at": str(product.created_at), 
                 "updated_at": str(product.updated_at)
                 } 
                for product in products]
    except Exception as e:
        return {"error": f"Failed to fetch products: {str(e)}"}
    
@tool
def get_product_by_id(product_id: int) -> Dict[str, Any]:
    """
    Retrieve a product by its ID.
    
    Args:
        product_id: ID of the product to retrieve
    
    Returns:
        Product dictionary with id, title, handle, and status
    """
    try:
        product = shopify.Product.find(product_id)
        if not product:
            return {"error": "Product not found"}
        return {
            "id": product.id,
            "title": product.title,
            "handle": product.handle,
            "status": product.status,
            "vendor": product.vendor,
            "product_type": product.product_type,
            "created_at": str(product.created_at),
            "updated_at": str(product.updated_at)
        }
    except Exception as e:
        return {"error": f"Failed to fetch product {product_id}: {str(e)}"}
    
