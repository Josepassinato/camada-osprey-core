"""
Admin Package

This package contains administrative functionality including security
management, knowledge base administration, and product management.

Modules:
    - security.py: Admin security and access control
    - knowledge_base.py: Knowledge base administration
    - products.py: Product and package management
"""

from backend.admin.security import (
    require_admin,
    require_superadmin,
    get_current_user,
    log_admin_action,
    get_admin_audit_log,
    check_admin_rate_limit,
    AuditAction,
    UserRole,
)

from backend.admin.knowledge_base import (
    save_pdf_to_knowledge_base,
    list_knowledge_base_documents,
    get_knowledge_base_document,
    delete_knowledge_base_document,
    search_knowledge_base,
    get_knowledge_base_stats,
)

from backend.admin.products import (
    initialize_products_in_db,
    get_all_products,
    get_product,
    update_product_price,
    sync_product_to_stripe,
    sync_all_products_to_stripe,
    get_product_for_checkout,
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
