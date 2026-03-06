"""
Admin Package

This package contains administrative functionality including security
management, knowledge base administration, and product management.

Modules:
    - security.py: Admin security and access control
    - knowledge_base.py: Knowledge base administration
    - products.py: Product and package management
"""

from backend.admin.knowledge_base import (
    delete_knowledge_base_document,
    get_knowledge_base_document,
    get_knowledge_base_stats,
    list_knowledge_base_documents,
    save_pdf_to_knowledge_base,
    search_knowledge_base,
)
from backend.admin.products import (
    get_all_products,
    get_product,
    get_product_for_checkout,
    initialize_products_in_db,
    sync_all_products_to_stripe,
    sync_product_to_stripe,
    update_product_price,
)
from backend.admin.security import (
    AuditAction,
    UserRole,
    check_admin_rate_limit,
    get_admin_audit_log,
    get_current_user,
    log_admin_action,
    require_admin,
    require_superadmin,
)

__all__ = [
    # Security
    "require_admin",
    "require_superadmin",
    "get_current_user",
    "log_admin_action",
    "get_admin_audit_log",
    "check_admin_rate_limit",
    "AuditAction",
    "UserRole",
    # Knowledge Base
    "save_pdf_to_knowledge_base",
    "list_knowledge_base_documents",
    "get_knowledge_base_document",
    "delete_knowledge_base_document",
    "search_knowledge_base",
    "get_knowledge_base_stats",
    # Products
    "initialize_products_in_db",
    "get_all_products",
    "get_product",
    "update_product_price",
    "sync_product_to_stripe",
    "sync_all_products_to_stripe",
    "get_product_for_checkout",
]
