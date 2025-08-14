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
    
@tool
def get_customers(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve customers from Shopify store.
    
    Args:
        limit: Maximum number of customers to retrieve (default: 10)
    
    Returns:
        List of customer dictionaries with id, email, first_name, last_name, and created_at
    """
    try:
        customers = shopify.Customer.find(limit=limit)
        return [{
                "id": customer.id, 
                "email": customer.email, 
                "first_name": customer.first_name, 
                "last_name": customer.last_name, 
                "phone": customer.phone,
                "total_spent": customer.total_spent,
                "orders_count": customer.orders_count,
                "state": customer.state,
                "created_at": str(customer.created_at)
                } 
                for customer in customers]
    except Exception as e:
        return {"error": f"Failed to fetch customers: {str(e)}"}
    
@tool
def get_orders(limit: int = 10, status: str = "any") -> List[Dict[str, Any]]:
    """
    Retrieve orders from Shopify store.
    
    Args:
        limit: Maximum number of orders to retrieve (default: 10)
        status: Order status to filter by (default: "any"), Other options (open, closed, cancelled)
    
    Returns:
        List of order dictionaries including id, email, total_price, and created_at
    """
    try:
        params = {"limit": limit}
        if status != "any":
            params["status"] = status
            
        orders = shopify.Order.find(**params)
        return [{
                "id": order.id, 
                "email": order.email, 
                "total_price": order.total_price, 
                "created_at": str(order.created_at), 
                "financial_status": order.financial_status,
                "fulfillment_status": order.fulfillment_status,
                "created_at": str(order.created_at),
                "customer": {
                    "id": order.customer.id if order.customer else None,
                    "email": order.customer.email if order.customer else None,
                    "first_name": order.customer.first_name if order.customer else None,
                    "last_name": order.customer.last_name if order.customer else None
                } if order.customer else None
                } 
                for order in orders]
    except Exception as e:
        return {"error": f"Failed to fetch orders: {str(e)}"}
    
@tool
def update_product_inventory(variant_id: int, quantity: int) -> Dict[str, Any]:
    """
    Update inventory quantity for a product variant.
    
    Args:
        variant_id: ID of the product variant to update
        quantity: New inventory quantity
    
    Returns:
        Updated product variant dictionary with id, title, and inventory_quantity
    """
    try:
        variant = shopify.Variant.find(variant_id)
        if not variant:
            return {"error": "Variant not found"}
        
        variant.inventory_quantity = quantity
        if variant.save():
            return {
                "success": True,
                "variant_id": variant.id,
                "variant_title": variant.title,
                "new_quantity": variant.inventory_quantity,
                "message": f"Inventory updated successfully for variant {variant_id}"
            }
        else:
            return {"error": "Failed to update inventory"}
    except Exception as e:
        return {"error": f"Failed to update inventory for variant {variant_id}: {str(e)}"}