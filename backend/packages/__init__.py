"""
Package generation and payment packages module.

This package contains modules for generating USCIS application packages
and managing payment packages for different visa types.
"""

from .generator import USCISPackageGenerator, generate_final_package
from .payment_packages import (
    VISA_PACKAGES,
    calculate_final_price,
    get_all_packages,
    get_packages_by_category,
    get_visa_package,
    get_visa_price,
    validate_visa_code,
)

__all__ = [
    # Generator
    "USCISPackageGenerator",
    "generate_final_package",
    # Payment packages
    "VISA_PACKAGES",
    "get_visa_price",
    "get_visa_package",
    "get_all_packages",
    "get_packages_by_category",
    "validate_visa_code",
    "calculate_final_price",
]
