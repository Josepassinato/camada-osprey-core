#!/usr/bin/env python3
"""
Script to unblock IP addresses from the security system
"""

import sys
import os
sys.path.append('/app/backend')

from security_hardening import security_system

def unblock_test_ip():
    """Unblock the test IP that got blocked during testing"""
    
    # Get the current blocked IPs
    blocked_ips = security_system.blocked_ips.copy()
    
    print(f"Currently blocked IPs: {len(blocked_ips)}")
    for ip, block_until in blocked_ips.items():
        print(f"  - {ip}: blocked until {block_until}")
    
    # Unblock all IPs
    unblocked_count = 0
    for ip in list(blocked_ips.keys()):
        if security_system.unblock_ip(ip, "Testing Phase 4B corrections"):
            unblocked_count += 1
            print(f"✅ Unblocked {ip}")
    
    print(f"\n🎯 Total IPs unblocked: {unblocked_count}")
    print("✅ Ready for Phase 4B testing!")

if __name__ == "__main__":
    unblock_test_ip()