#!/usr/bin/env python3
"""
Customer_Group_Loyalty_Config.py
Combined Web + Mobile Automation: Customer Group + Loyalty Configuration + Customer Creation + Mobile Login
Complete workflow: 
1. Web: Login → Customer Group → Loyalty Configuration → Customer Creation (Browser stays open)
2. Mobile: Launch App → Login → OTP Capture → Wait
"""

import asyncio
import os
import sys
import subprocess
import re
import time
import random
import string
from datetime import datetime
from playwright.async_api import async_playwright
try:
    from PIL import Image
except ImportError:
    print("PIL not available, will use fallback method for file upload")

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header(message):
    print(f"{Colors.BLUE}[HEADER]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_fail(message):
    print(f"{Colors.RED}[FAIL]{Colors.NC} {message}")

def generate_unique_customer_group_name():
    """Generate a unique customer group name with 8-9 characters"""
    # Generate a random length between 8 and 9
    length = random.randint(8, 9)
    
    # Create a prefix for better readability
    prefix = "Loyalty"
    
    # Generate random characters for the remaining length
    remaining_length = length - len(prefix)
    if remaining_length > 0:
        # Use uppercase letters and numbers for uniqueness
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=remaining_length))
        unique_name = f"{prefix}{random_chars}"
    else:
        unique_name = prefix
    
    # Add timestamp suffix for additional uniqueness
    timestamp = datetime.now().strftime("%H%M%S")
    unique_name = f"{unique_name}_{timestamp}"
    
    return unique_name

def generate_unique_mobile_number():
    """Generate a unique 10-digit mobile number"""
    # Start with a valid mobile prefix (e.g., 5, 6, 7, 8, 9)
    valid_prefixes = ['5', '6', '7', '8', '9']
    prefix = random.choice(valid_prefixes)
    
    # Generate remaining 9 digits randomly
    remaining_digits = ''.join(random.choices(string.digits, k=9))
    
    # Combine prefix with remaining digits
    mobile_number = f"{prefix}{remaining_digits}"
    
    # Add timestamp suffix for additional uniqueness (optional, can be removed if you want exactly 10 digits)
    timestamp = datetime.now().strftime("%H%M")
    unique_mobile = f"{mobile_number}_{timestamp}"
    
    return unique_mobile

def generate_unique_customer_name():
    """Generate a unique customer name"""
    # Create a prefix for better readability
    prefix = "Customer"
    
    # Generate random characters for uniqueness
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    
    # Add timestamp suffix for additional uniqueness
    timestamp = datetime.now().strftime("%H%M%S")
    unique_customer_name = f"{prefix}{random_chars}_{timestamp}"
    
    return unique_customer_name

# ============================================================================
# WEB AUTOMATION FUNCTIONS
# ============================================================================

async def run_web_automation():
    """Run web automation using Playwright"""
    print_header("Starting Customer Group + Loyalty Configuration + Customer Creation Web Automation")
    
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=False, slow_mo=300)
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
            # Navigate to login page
            print_status("Navigating to login page...")
            await page.goto('http://digisol.loyaltyxpert.staging/auth/auth/login', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('domcontentloaded')
            print_success("Login page loaded")
            
            # Login process
            print_status("Starting login process...")
            
            # Find and fill username field
            username_selectors = [
                'input[name="username"]', 'input[name="email"]', 'input[type="email"]',
                'input[type="text"]', '#username', '#email', '.username', '.email',
                'input[placeholder*="username" i]', 'input[placeholder*="email" i]'
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    username_field = await page.query_selector(selector)
                    if username_field:
                        break
                except:
                    continue
            
            if not username_field:
                print_error("Username field not found")
                return False
            
            await username_field.click()
            await username_field.fill('ishita.popat@ecosmob.com')
            print_success("Username entered")
            
            # Find and fill password field
            password_selectors = [
                'input[name="password"]', 'input[type="password"]', '#password',
                '.password', 'input[placeholder*="password" i]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    password_field = await page.query_selector(selector)
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print_error("Password field not found")
                return False
            
            await password_field.click()
            await password_field.fill('Test@123')
            print_success("Password entered")
            
            # Find and click login button
            login_selectors = [
                'button[type="submit"]', 'input[type="submit"]', '.login-btn',
                '#login', 'button:has-text("Login")', 'button:has-text("Sign In")'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    login_button = await page.query_selector(selector)
                    if login_button:
                        break
                except:
                    continue
            
            if not login_button:
                print_error("Login button not found")
                return False
            
            await login_button.click()
            print_success("Login button clicked")
            
            # Wait after login
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Post-login page loaded")
            
            # ============================================================================
            # PHASE 1: CUSTOMER GROUP OPERATIONS (from Customer_Group.py)
            # ============================================================================
            print_header("PHASE 1: CUSTOMER GROUP OPERATIONS")
            
            # Find and click search box from left navigation
            print_status("Looking for search box...")
            search_box_selectors = [
                'input[placeholder*="search" i]', 'input[type="search"]', '.search-box input',
                '.search input', '[data-testid="search"]', 'input[aria-label*="search" i]',
                '.nav input[type="text"]', '.sidebar input[type="text"]', 'input[name="search"]'
            ]
            
            search_box = None
            for selector in search_box_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    search_box = await page.query_selector(selector)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print_error("Search box not found")
                return False
            
            await search_box.click()
            print_success("Search box clicked")
            
            # Type "Cus" in search box gradually with pauses
            print_status("Typing 'Cus' gradually...")
            search_text = 'Cus'
            for i in range(len(search_text)):
                await search_box.type(search_text[i])
                await page.wait_for_timeout(200)  # 200ms pause between each character
            
            print_success("Typed 'Cus' gradually with pauses")
            
            # Wait a moment for the interface to update after typing
            await page.wait_for_timeout(1000)
            
            # Navigate to the customer category page
            print_status("Navigating to customer category page...")
            await page.goto('http://digisol.loyaltyxpert.staging/customer/customer-category/index', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Customer category page loaded")
            
            # Verify we've navigated to the correct customer category page
            current_url = page.url
            if 'customer-category' in current_url:
                print_success("Successfully navigated to customer category page")
                print(f"Current URL: {current_url}")
            else:
                print_error("Navigation to customer category page failed")
                return False
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Click "ADD NEW" button
            print_status("Looking for ADD NEW button...")
            add_new_selectors = [
                'button:has-text("ADD NEW")', 'a:has-text("ADD NEW")', '.btn:has-text("ADD NEW")',
                '[data-testid="add-new"]', '.add-new-btn', 'button[title*="ADD NEW" i]',
                'a[title*="ADD NEW" i]', '.btn-primary:has-text("ADD NEW")'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("ADD NEW button clicked")
            
            # Wait for form to load
            await page.wait_for_timeout(3000)
            
            # Fill Customer Group Name field
            print_status("Filling Customer Group Name field...")
            name_selectors = [
                'input[name*="name" i]', 'input[id*="name" i]', '#customercategory-name',
                'input[placeholder*="name" i]', '.customer-group-name input', 'input[name="CustomerCategory[name]"]'
            ]
            
            name_field = None
            for selector in name_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    name_field = await page.query_selector(selector)
                    if name_field:
                        break
                except:
                    continue
            
            if not name_field:
                print_error("Customer Group Name field not found")
                return False
            
            await name_field.click()
            unique_name = generate_unique_customer_group_name()
            await name_field.fill(unique_name)
            print_success(f"Customer Group Name filled with unique name: '{unique_name}'")
            
            # Select Status dropdown - "Active"
            print_status("Selecting Status dropdown...")
            status_selectors = [
                '#select2-customercategory-cust_category_status-container',
                'span[title="Select Status"]', '.select2-selection__rendered[title="Select Status"]',
                '[id*="status"][class*="select2"]', '.select2-container:has-text("Select Status")'
            ]
            
            status_dropdown = None
            for selector in status_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    status_dropdown = await page.query_selector(selector)
                    if status_dropdown:
                        break
                except:
                    continue
            
            if not status_dropdown:
                print_error("Status dropdown not found")
                return False
            
            await status_dropdown.click()
            await page.wait_for_timeout(1000)
            
            # Select "Active" option
            active_selectors = [
                'li:has-text("Active")', '.select2-results__option:has-text("Active")',
                '[data-select2-id*="active" i]', 'li[title="Active"]'
            ]
            
            active_option = None
            for selector in active_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    active_option = await page.query_selector(selector)
                    if active_option:
                        break
                except:
                    continue
            
            if not active_option:
                print_error("Active option not found in Status dropdown")
                return False
            
            await active_option.click()
            print_success("Status set to 'Active'")
            
            # Select Earning Options dropdown - multiple selections
            print_status("Selecting Earning Options dropdown...")
            earning_selectors = [
                'input[placeholder="Select Earning Options"]', '.select2-search__field[placeholder*="Earning Options"]',
                'input[aria-autocomplete="list"][placeholder*="Earning Options"]', '.select2-search__field'
            ]
            
            earning_dropdown = None
            for selector in earning_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    earning_dropdown = await page.query_selector(selector)
                    if earning_dropdown:
                        break
                except:
                    continue
            
            if not earning_dropdown:
                print_error("Earning Options dropdown not found")
                return False
            
            # Simplified function to select only "Scan QR Code"
            async def select_scan_qr_code():
                try:
                    print_status("Selecting 'Scan QR Code' from Earning Options...")
                    
                    # Click on the earning dropdown to open it
                    await earning_dropdown.click()
                    await page.wait_for_timeout(2000)
                    
                    # Try multiple selectors for "Scan QR Code" option
                    scan_qr_selectors = [
                        'li:has-text("Scan QR Code")', 
                        '.select2-results__option:has-text("Scan QR Code")',
                        '[data-select2-id*="scan" i]', 
                        'li[title="Scan QR Code"]',
                        '.select2-results li:has-text("Scan QR Code")',
                        '[role="option"]:has-text("Scan QR Code")'
                    ]
                    
                    option_found = False
                    for selector in scan_qr_selectors:
                        try:
                            await page.wait_for_selector(selector, state='visible', timeout=3000)
                            option_element = await page.query_selector(selector)
                            if option_element:
                                await option_element.click()
                                print_success("Selected 'Scan QR Code'")
                                option_found = True
                                await page.wait_for_timeout(1500)  # Wait for selection to register
                                break
                        except Exception as e:
                            continue
                    
                    if not option_found:
                        print_warning("'Scan QR Code' option not found, trying alternative approach...")
                        
                        # Alternative: try to type the option name
                        try:
                            await earning_dropdown.click()
                            await page.wait_for_timeout(500)
                            await earning_dropdown.type("Scan QR Code")
                            await page.wait_for_timeout(1000)
                            
                            # Look for the typed option
                            typed_option_selectors = [
                                'li:has-text("Scan QR Code")', 
                                '.select2-results__option:has-text("Scan QR Code")'
                            ]
                            
                            for selector in typed_option_selectors:
                                try:
                                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                                    typed_option = await page.query_selector(selector)
                                    if typed_option:
                                        await typed_option.click()
                                        print_success("Selected 'Scan QR Code' (via typing)")
                                        await page.wait_for_timeout(1500)
                                        break
                                except:
                                    continue
                        except Exception as e:
                            print_warning(f"Alternative approach failed for 'Scan QR Code': {e}")
                    
                    print_success("Earning options selection completed")
                    return True
                    
                except Exception as e:
                    print_error(f"Error in earning options selection: {e}")
                    return False
            
            # Execute the earning options selection (only Scan QR Code)
            await select_scan_qr_code()
            
            # Select Wallet Type dropdown - "Primary Wallet"
            print_status("Selecting Wallet Type dropdown...")
            wallet_selectors = [
                '#select2-customercategory-wallet_type-container',
                'span[title="Secondary Wallet"]', '.select2-selection__rendered[title="Secondary Wallet"]',
                '[id*="wallet"][class*="select2"]', '.select2-container:has-text("Secondary Wallet")'
            ]
            
            wallet_dropdown = None
            for selector in wallet_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    wallet_dropdown = await page.query_selector(selector)
                    if wallet_dropdown:
                        break
                except:
                    continue
            
            if not wallet_dropdown:
                print_error("Wallet Type dropdown not found")
                return False
            
            await wallet_dropdown.click()
            await page.wait_for_timeout(1000)
            
            # Select "Primary Wallet" option
            primary_wallet_selectors = [
                'li:has-text("Primary Wallet")', '.select2-results__option:has-text("Primary Wallet")',
                '[data-select2-id*="primary" i]', 'li[title="Primary Wallet"]'
            ]
            
            primary_wallet_option = None
            for selector in primary_wallet_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    primary_wallet_option = await page.query_selector(selector)
                    if primary_wallet_option:
                        break
                except:
                    continue
            
            if not primary_wallet_option:
                print_error("Primary Wallet option not found")
                return False
            
            await primary_wallet_option.click()
            print_success("Wallet Type set to 'Primary Wallet'")
            
            # Fill Hierarchy Rank field with "80"
            print_status("Filling Hierarchy Rank field...")
            hierarchy_rank_selectors = [
                '#customercategory-hierarchy_rank', 'input[name="CustomerCategory[hierarchy_rank]"]',
                'input[placeholder="Hierarchy Rank"]', 'input[type="number"][id*="hierarchy_rank"]'
            ]
            
            hierarchy_rank_field = None
            for selector in hierarchy_rank_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    hierarchy_rank_field = await page.query_selector(selector)
                    if hierarchy_rank_field:
                        break
                except:
                    continue
            
            if not hierarchy_rank_field:
                print_error("Hierarchy Rank field not found")
                return False
            
            # Scroll to make sure the field is visible
            await page.evaluate("(element) => element.scrollIntoView({block: 'center'});", hierarchy_rank_field)
            await page.wait_for_timeout(1000)
            
            # Use JavaScript to click and fill the field to avoid overlapping elements
            await page.evaluate("(element) => { element.click(); element.focus(); }", hierarchy_rank_field)
            await page.wait_for_timeout(500)
            await page.evaluate("(element) => { element.value = '80'; element.dispatchEvent(new Event('input', { bubbles: true })); }", hierarchy_rank_field)
            print_success("Hierarchy Rank field filled with '80'")
            
            # Scroll down a little after Point Transfer step
            print_status("Scrolling down after Point Transfer step...")
            await page.evaluate("window.scrollBy(0, 300)")
            await page.wait_for_timeout(1000)
            print_success("Scrolled down successfully")
            
            # Scroll down more for additional fields
            print_status("Scrolling down for additional fields...")
            await page.evaluate("window.scrollBy(0, 400)")
            await page.wait_for_timeout(1000)
            print_success("Scrolled down for additional fields")
            
            # Click radio button for "is_required_all" with value "1"
            print_status("Clicking radio button for is_required_all (value=1)...")
            radio_selectors = [
                'input[type="radio"][name="CustomerCategory[is_required_all]"][value="1"]',
                'input[type="radio"][value="1"]',
                'input[name*="is_required_all"][value="1"]'
            ]
            
            radio_button = None
            for selector in radio_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    radio_button = await page.query_selector(selector)
                    if radio_button:
                        break
                except:
                    continue
            
            if not radio_button:
                print_error("Radio button for is_required_all (value=1) not found")
                return False
            
            await radio_button.click()
            print_success("Radio button for is_required_all (value=1) clicked")
            
            # Click checkbox with label for "1"
            print_status("Clicking checkbox with label for '1'...")
            checkbox1_selectors = [
                'label[for="1"]', 'label.control-label.text-bold-600.check-container',
                'input[type="checkbox"][id="1"]', 'input[name*="1"]'
            ]
            
            checkbox1 = None
            for selector in checkbox1_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    checkbox1 = await page.query_selector(selector)
                    if checkbox1:
                        break
                except:
                    continue
            
            if not checkbox1:
                print_error("Checkbox with label for '1' not found")
                return False
            
            await checkbox1.click()
            print_success("Checkbox with label for '1' clicked")
            
            # Click checkbox with label for "is_mandatory_1"
            print_status("Clicking checkbox with label for 'is_mandatory_1'...")
            checkbox_mandatory_selectors = [
                'label[for="is_mandatory_1"]', 'label.control-label.check-container.mandatory-mr-left',
                'input[type="checkbox"][id="is_mandatory_1"]', 'input[name*="is_mandatory_1"]'
            ]
            
            checkbox_mandatory = None
            for selector in checkbox_mandatory_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    checkbox_mandatory = await page.query_selector(selector)
                    if checkbox_mandatory:
                        break
                except:
                    continue
            
            if not checkbox_mandatory:
                print_error("Checkbox with label for 'is_mandatory_1' not found")
                return False
            
            await checkbox_mandatory.click()
            print_success("Checkbox with label for 'is_mandatory_1' clicked")
            
            # Click Add button
            print_status("Clicking Add button...")
            add_button_selectors = [
                'button[type="submit"]', 'input[type="submit"]', '.btn-primary',
                'button:has-text("Add")', 'button:has-text("Submit")', '.submit-btn'
            ]
            
            add_button = None
            for selector in add_button_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_button = await page.query_selector(selector)
                    if add_button:
                        break
                except:
                    continue
            
            if not add_button:
                print_error("Add button not found")
                return False
            
            await add_button.click()
            print_success("Add button clicked")
            
            # Wait after clicking Add button
            print_status("Waiting 8 seconds after clicking Add button...")
            await page.wait_for_timeout(8000)
            print_success("Waited 8 seconds after Add button click")
            
            print_success("Customer Group form filled successfully")
            
            # ============================================================================
            # PHASE 2: LOYALTY CONFIGURATION OPERATIONS (from Loyalty_Confirgration.py)
            # ============================================================================
            print_header("PHASE 2: LOYALTY CONFIGURATION OPERATIONS")
            
            # Navigate to configuration groups page
            print_status("Navigating to configuration groups page...")
            await page.goto('http://digisol.loyaltyxpert.staging/configurationgroups/configuration-groups/index', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Configuration groups page loaded")
            
            # Verify we've navigated to the correct configuration groups page
            current_url = page.url
            if 'configuration-groups' in current_url:
                print_success("Successfully navigated to configuration groups page")
                print(f"Current URL: {current_url}")
            else:
                print_error("Navigation to configuration groups page failed")
                return False
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Click "ADD NEW" button
            print_status("Looking for ADD NEW button...")
            add_new_selectors = [
                'button:has-text("ADD NEW")', 'a:has-text("ADD NEW")', '.btn:has-text("ADD NEW")',
                '[data-testid="add-new"]', '.add-new-btn', 'button[title*="ADD NEW" i]',
                'a[title*="ADD NEW" i]', '.btn-primary:has-text("ADD NEW")'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("ADD NEW button clicked")
            
            # Wait for form to load and ensure it's fully rendered
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Fill Configuration Group Name field
            print_status("Filling Configuration Group Name field...")
            group_name_selectors = [
                '#configurationgroups-group_name', 'input[name="ConfigurationGroups[group_name]"]',
                'input[placeholder="Configuration Group Name"]', 'input[type="text"][id*="group_name"]'
            ]
            
            group_name_field = None
            for selector in group_name_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    group_name_field = await page.query_selector(selector)
                    if group_name_field:
                        break
                except:
                    continue
            
            if not group_name_field:
                print_error("Configuration Group Name field not found")
                return False
            
            await group_name_field.click()
            await group_name_field.fill(unique_name)
            print_success(f"Configuration Group Name filled with unique name: '{unique_name}'")
            
            # Use Tab navigation to move to next fields
            print_status("Using Tab navigation to fill remaining fields...")
            
            # Press Tab to move to Description field
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('Hello I M Automation')
            print_success("Description field filled with 'Hello I M Automation'")
            
            # Press Tab to move to Redemption Target field
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('90')
            print_success("Redemption Target field filled with '90'")
            
            # Press Tab to move to Loyalty Rate field
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('2')
            print_success("Loyalty Rate field filled with '2'")
            
            # Press Tab to move to Customer Group dropdown
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            
            # Select Customer Group from dropdown
            print_status("Selecting Customer Group from dropdown...")
            customer_group_selectors = [
                'input[placeholder="Select Customer Group"]', '.select2-search__field',
                'input[aria-autocomplete="list"]', '.select2-search__field'
            ]
            
            customer_group_dropdown = None
            for selector in customer_group_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    customer_group_dropdown = await page.query_selector(selector)
                    if customer_group_dropdown:
                        break
                except:
                    continue
            
            if customer_group_dropdown:
                await customer_group_dropdown.click()
                await page.wait_for_timeout(1000)
                
                # Look for the unique name option
                unique_name_selectors = [
                    f'li:has-text("{unique_name}")', f'.select2-results__option:has-text("{unique_name}")',
                    f'[data-select2-id*="{unique_name}" i]', f'li[title="{unique_name}"]'
                ]
                
                unique_name_option = None
                for selector in unique_name_selectors:
                    try:
                        await page.wait_for_selector(selector, state='visible', timeout=2000)
                        unique_name_option = await page.query_selector(selector)
                        if unique_name_option:
                            break
                    except:
                        continue
                
                if unique_name_option:
                    await unique_name_option.click()
                    print_success(f"Selected '{unique_name}' from Customer Group dropdown")
                else:
                    print_warning(f"'{unique_name}' option not found, continuing...")
            else:
                print_warning("Customer Group dropdown not found, continuing...")
            
            # Press Tab to move to Create button
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            
            # Click Create button
            print_status("Clicking Create button...")
            create_button_selectors = [
                'button[type="submit"]', 'input[type="submit"]', '.btn-primary',
                'button:has-text("Create")', 'button:has-text("Submit")', '.submit-btn'
            ]
            
            create_button = None
            for selector in create_button_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    create_button = await page.query_selector(selector)
                    if create_button:
                        break
                except:
                    continue
            
            if not create_button:
                print_error("Create button not found")
                return False
            
            await create_button.click()
            print_success("Create button clicked")
            
            # Wait after clicking Create button
            print_status("Waiting 5 seconds after clicking Create button...")
            await page.wait_for_timeout(5000)
            print_success("Waited 5 seconds after Create button click")
            
            print_success("Loyalty Configuration form filled successfully")
            
            # ============================================================================
            # PHASE 3: CUSTOMER CREATION OPERATIONS (from Customer_Create.py)
            # ============================================================================
            print_header("PHASE 3: CUSTOMER CREATION OPERATIONS")
            
            # Navigate to customer master page
            print_status("Navigating to customer master page...")
            await page.goto('http://digisol.loyaltyxpert.staging/customer/customer-master/index', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Customer master page loaded")
            
            # Verify we've navigated to the correct customer master page
            current_url = page.url
            if 'customer-master' in current_url:
                print_success("Successfully navigated to customer master page")
                print(f"Current URL: {current_url}")
            else:
                print_error("Navigation to customer master page failed")
                return False
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Click "ADD NEW" button
            print_status("Looking for ADD NEW button...")
            add_new_selectors = [
                'button:has-text("ADD NEW")', 'a:has-text("ADD NEW")', '.btn:has-text("ADD NEW")',
                '[data-testid="add-new"]', '.add-new-btn', 'button[title*="ADD NEW" i]',
                'a[title*="ADD NEW" i]', '.btn-primary:has-text("ADD NEW")'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("ADD NEW button clicked")
            
            # Wait for form to load and ensure it's fully rendered
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Fill Customer Mobile Number field
            print_status("Filling Customer Mobile Number field...")
            mobile_selectors = [
                '#customermaster-cust_mobile_number', 'input[name="CustomerMaster[cust_mobile_number]"]',
                'input[placeholder="Customer Mobile Number"]', 'input[id*="cust_mobile_number"]'
            ]
            
            mobile_field = None
            for selector in mobile_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    mobile_field = await page.query_selector(selector)
                    if mobile_field:
                        break
                except:
                    continue
            
            if not mobile_field:
                print_error("Customer Mobile Number field not found")
                return False
            
            await mobile_field.click()
            unique_mobile = generate_unique_mobile_number()
            await mobile_field.fill(unique_mobile)
            print_success(f"Customer Mobile Number filled with unique mobile: '{unique_mobile}'")
            
            # Use Tab navigation to move to next fields
            print_status("Using Tab navigation to fill remaining fields...")
            
            # Press Tab to move to next field and type unique customer name
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            unique_customer_name = generate_unique_customer_name()
            await page.keyboard.type(unique_customer_name)
            print_success(f"Customer Name field filled with unique customer name: '{unique_customer_name}'")
            
            # Press Tab to move to next field and type "Ecosmob"
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('Ecosmob')
            print_success("Company field filled with 'Ecosmob'")
            
            # Press Tab to move to Customer Group dropdown
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            
            # Select Customer Group from dropdown
            print_status("Selecting Customer Group from dropdown...")
            customer_group_selectors = [
                '#select2-customermaster-cust_category_id-container', 
                'span[title="Select Customer Group"]',
                '.select2-selection__rendered[title="Select Customer Group"]'
            ]
            
            customer_group_dropdown = None
            for selector in customer_group_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    customer_group_dropdown = await page.query_selector(selector)
                    if customer_group_dropdown:
                        break
                except:
                    continue
            
            if not customer_group_dropdown:
                print_error("Customer Group dropdown not found")
                return False
            
            await customer_group_dropdown.click()
            print_success("Customer Group dropdown clicked")
            
            # Wait for dropdown to open and search for the unique customer group
            await page.wait_for_timeout(1000)
            
            # Look for the search field within the dropdown
            search_field_selectors = [
                '.select2-search__field',
                'input[type="search"]',
                '.select2-search input',
                'input[placeholder*="search" i]'
            ]
            
            search_field = None
            for selector in search_field_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    search_field = await page.query_selector(selector)
                    if search_field:
                        break
                except:
                    continue
            
            if search_field:
                # Type the unique name in the search field
                await search_field.fill(unique_name)
                print_success(f"Typed '{unique_name}' in search field")
                
                # Wait for search results to appear
                await page.wait_for_timeout(1000)
                
                # Look for the specific option with the unique name
                option_selectors = [
                    f'li:has-text("{unique_name}")',
                    f'.select2-results__option:has-text("{unique_name}")',
                    f'[data-select2-id*="{unique_name}" i]',
                    f'li[title="{unique_name}"]',
                    f'.select2-results li:has-text("{unique_name}")'
                ]
                
                option_found = False
                for selector in option_selectors:
                    try:
                        await page.wait_for_selector(selector, state='visible', timeout=2000)
                        option_element = await page.query_selector(selector)
                        if option_element:
                            await option_element.click()
                            print_success(f"Selected '{unique_name}' from dropdown options")
                            option_found = True
                            break
                    except:
                        continue
                
                if not option_found:
                    # Fallback: try pressing Enter after typing
                    await page.keyboard.press('Enter')
                    print_success(f"Used fallback method to select '{unique_name}'")
            else:
                # Fallback: use keyboard navigation if search field not found
                await page.keyboard.type(unique_name)
                await page.wait_for_timeout(1000)
                await page.keyboard.press('Enter')
                print_success(f"Used keyboard navigation to select '{unique_name}'")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Press Tab 3 times to move to next fields
            print_status("Pressing Tab 3 times to move to next fields...")
            for i in range(3):
                await page.keyboard.press('Tab')
                await page.wait_for_timeout(300)
                print_status(f"Tab {i+1}/3 pressed")
            
            # Type unique additional phone number
            print_status("Typing unique additional phone number...")
            unique_additional_mobile = generate_unique_mobile_number()
            await page.keyboard.type(unique_additional_mobile)
            print_success(f"Additional phone field filled with unique mobile: '{unique_additional_mobile}'")
            
            # Press Tab to move to address field
            print_status("Pressing Tab to move to address field...")
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('Ahmedabad India')
            print_success("Address field filled with 'Ahmedabad India'")
            
            # Wait a moment for the address to be properly entered
            await page.wait_for_timeout(1000)
            
            # Scroll down to find the Aadhaar/PAN dropdown
            print_status("Scrolling down to find Aadhaar/PAN dropdown...")
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(1000)
            
            # Find and click the Aadhaar/PAN dropdown
            print_status("Looking for Aadhaar/PAN dropdown...")
            aadhaar_selectors = [
                '#select2-customermaster-is_aadhaar_or_pan_linked-container',
                'span[title="Select"]',
                '.select2-selection__rendered[title="Select"]'
            ]
            
            aadhaar_dropdown = None
            for selector in aadhaar_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    aadhaar_dropdown = await page.query_selector(selector)
                    if aadhaar_dropdown:
                        break
                except:
                    continue
            
            if not aadhaar_dropdown:
                print_error("Aadhaar/PAN dropdown not found")
                return False
            
            await aadhaar_dropdown.click()
            print_success("Aadhaar/PAN dropdown clicked")
            
            # Wait for dropdown to open and select "Yes"
            await page.wait_for_timeout(1000)
            await page.keyboard.type('Yes')
            await page.keyboard.press('Enter')
            print_success("Aadhaar/PAN linked set to 'Yes'")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Click Add button
            print_status("Looking for Add button...")
            add_selectors = [
                'button:has-text("Add")', 'button:has-text("Save")', 'button:has-text("Submit")',
                'input[type="submit"][value*="Add" i]', 'input[type="submit"][value*="Save" i]',
                '.btn-primary:has-text("Add")', '.btn-success:has-text("Add")',
                'button[type="submit"]', 'input[type="submit"]'
            ]
            
            add_button = None
            for selector in add_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_button = await page.query_selector(selector)
                    if add_button:
                        break
                except:
                    continue
            
            if not add_button:
                print_error("Add button not found")
                return False
            
            await add_button.click()
            print_success("Add button clicked")
            
            # Wait for form submission
            await page.wait_for_timeout(3000)
            
            print_success("Customer Creation form filled successfully")
            
            # ============================================================================
            # PHASE 4: MOBILE AUTOMATION (App Launch + Login + OTP Capture)
            # ============================================================================
            print_header("PHASE 4: MOBILE AUTOMATION")
            
            # Setup Android environment
            setup_android_environment()
            
            # Check device connection
            if check_device():
                mobile_success = run_mobile_automation(unique_mobile)
                if mobile_success:
                    print_success("🎉 Mobile automation completed successfully!")
                else:
                    print_error("❌ Mobile automation failed")
                    return False
            else:
                print_error("❌ Cannot proceed with mobile automation - no device connected")
                return False
            
            # ============================================================================
            # PHASE 5: KYC WEB AUTOMATION (Integrated into main web flow)
            # ============================================================================
            print_header("PHASE 5: KYC WEB AUTOMATION")
            
            # Navigate to Customer KYC page
            print_status("Navigating to Customer KYC page...")
            await page.goto('http://digisol.loyaltyxpert.staging/customer/customer-kyc/index', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('domcontentloaded')
            print_success("Customer KYC page loaded")
            
            # Click ADD NEW button
            print_status("Looking for ADD NEW button...")
            add_new_selectors = [
                'button:has-text("ADD NEW")', 'button:has-text("Add New")', 'button:has-text("Add")',
                'a:has-text("ADD NEW")', 'a:has-text("Add New")', 'a:has-text("Add")',
                '.btn-primary:has-text("ADD NEW")', '.btn-success:has-text("ADD NEW")',
                'input[value="ADD NEW"]', 'input[value="Add New"]'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("ADD NEW button clicked")
            
            # Wait for form to load
            await page.wait_for_timeout(2000)
            
            # Select Customer Member dropdown
            print_status("Selecting Customer Member dropdown...")
            customer_member_selectors = [
                '#select2-customer_member-container', 
                'span[title="Select"]',
                '.select2-selection__rendered[title="Select"]',
                'span.select2-selection__rendered',
                'div[role="combobox"]',
                'select[name*="customer_member"]',
                'select[id*="customer_member"]'
            ]
            
            customer_member_dropdown = None
            for selector in customer_member_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    customer_member_dropdown = await page.query_selector(selector)
                    if customer_member_dropdown:
                        break
                except:
                    continue
            
            if not customer_member_dropdown:
                print_error("Customer Member dropdown not found")
                return False
            
            await customer_member_dropdown.click()
            print_success("Customer Member dropdown clicked")
            
            # Wait for dropdown to open and type unique name
            await page.wait_for_timeout(1000)
            await page.keyboard.type(unique_name)
            # Wait 2 seconds after typing before pressing Enter
            await page.wait_for_timeout(2000)
            await page.keyboard.press('Enter')
            print_success(f"Customer Member '{unique_name}' selected")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Select KYC Document Type dropdown
            print_status("Selecting KYC Document Type dropdown...")
            kyc_doc_type_selectors = [
                '#select2-kyc_doc_type-container', 
                'span[title="Select Type"]',
                '.select2-selection__rendered[title="Select Type"]',
                'span.select2-selection__rendered',
                'div[role="combobox"]',
                'select[name*="kyc_doc_type"]',
                'select[id*="kyc_doc_type"]',
                'input[placeholder*="Select Type"]',
                'input[placeholder*="Document Type"]'
            ]
            
            kyc_doc_type_dropdown = None
            for selector in kyc_doc_type_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    kyc_doc_type_dropdown = await page.query_selector(selector)
                    if kyc_doc_type_dropdown:
                        print_success(f"Found KYC Document Type dropdown with selector: {selector}")
                        break
                except Exception as e:
                    print_warning(f"Selector {selector} failed: {e}")
                    continue
            
            if not kyc_doc_type_dropdown:
                print_error("KYC Document Type dropdown not found with any selector")
                return False
            
            await kyc_doc_type_dropdown.click()
            print_success("KYC Document Type dropdown clicked")
            
            # Wait for dropdown to open and select "PAN CARD"
            await page.wait_for_timeout(1000)
            await page.keyboard.type('PAN CARD')
            await page.keyboard.press('Enter')
            print_success("KYC Document Type 'PAN CARD' selected")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Press Tab to move to next field
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            
            # Type PAN number "MBGPK6487E"
            await page.keyboard.type('MBGPK6487E')
            print_success("PAN number 'MBGPK6487E' entered")
            
            # Press Tab only after PAN number entry
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(300)
            print_success("Tab pressed after PAN number entry")
            
            # After Tab, handle file upload for image/document
            print_status("Handling file upload after Tab key...")
            
            # Look for file input field
            file_input_selectors = [
                '#customerkyc-kyc_doc_proof',  # Specific ID from the page
                'input[type="file"]', 'input[accept*="image"]', 'input[accept*=".png"]',
                'input[accept*=".jpg"]', 'input[accept*=".jpeg"]', 'input[accept*=".pdf"]',
                'input[name*="file"]', 'input[name*="document"]', 'input[name*="image"]',
                'input[id*="file"]', 'input[id*="document"]', 'input[id*="image"]'
            ]
            
            file_input = None
            for selector in file_input_selectors:
                try:
                    # Try to find the file input without waiting for visibility since it might be hidden
                    file_input = await page.query_selector(selector)
                    if file_input:
                        print_success(f"Found file input with selector: {selector}")
                        break
                except Exception as e:
                    print_warning(f"Selector {selector} failed: {e}")
                    continue
            
            if file_input:
                # Create a sample image file for upload
                print_status("Creating sample image file for upload...")
                try:
                    # Create a simple sample image
                    sample_image_path = "sample_image.png"
                    
                    # Try to create a sample image using PIL, fallback to basic file creation
                    try:
                        from PIL import Image, ImageDraw
                        # Create a simple image
                        img = Image.new('RGB', (100, 100), color='red')
                        draw = ImageDraw.Draw(img)
                        draw.text((10, 40), 'Sample', fill='white')
                        img.save(sample_image_path)
                        print_success(f"Created sample image: {sample_image_path}")
                    except ImportError:
                        # Fallback: create a basic file
                        with open(sample_image_path, 'w') as f:
                            f.write("Sample image content")
                        print_success(f"Created basic sample file: {sample_image_path}")
                    
                    # Upload the file
                    await file_input.set_input_files(sample_image_path)
                    print_success(f"File uploaded successfully: {sample_image_path}")
                    
                    # Wait for upload to complete
                    await page.wait_for_timeout(2000)
                    
                except Exception as e:
                    print_error(f"File upload failed: {e}")
                    return False
            else:
                print_error("File input field not found")
                return False
            
            print_success("File upload completed successfully")
            
            # Click Add button to submit the form
            print_status("Looking for Add button to submit form...")
            add_button_selectors = [
                'button:has-text("Add")', 'button:has-text("Save")', 'button:has-text("Submit")',
                'input[type="submit"][value*="Add" i]', 'input[type="submit"][value*="Save" i]',
                '.btn-primary:has-text("Add")', '.btn-success:has-text("Add")',
                'button[type="submit"]', 'input[type="submit"]'
            ]
            
            add_button = None
            for selector in add_button_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_button = await page.query_selector(selector)
                    if add_button:
                        print_success(f"Found Add button with selector: {selector}")
                        break
                except Exception as e:
                    print_warning(f"Selector {selector} failed: {e}")
                    continue
            
            if not add_button:
                print_error("Add button not found")
                return False
            
            # Click the Add button
            await add_button.click()
            print_success("Add button clicked successfully")
            
            # Wait 5 seconds after clicking Add button
            print_status("Waiting 5 seconds after form submission...")
            await page.wait_for_timeout(5000)
            print_success("Waited 5 seconds after form submission")
            
            print_success("KYC Web automation completed")
            
            # ============================================================================
            # PHASE 6: MOBILE KYC CHECK AUTOMATION
            # ============================================================================
            print_header("PHASE 6: MOBILE KYC CHECK AUTOMATION")
            
            # Setup Android environment
            setup_android_environment()
            
            # Check device connection
            if check_device():
                print_status("Starting Mobile KYC Check Automation...")
                
                try:
                    # Step 1: Launch loyalty application
                    print_status("Launching loyalty application...")
                    launch_result = launch_loyalty_app()
                    if not launch_result:
                        print_error("Failed to launch loyalty application")
                        return False
                    
                    # Step 2: Wait 10 seconds after launch
                    print_status("Waiting 10 seconds after launch...")
                    time.sleep(10)
                    
                    # Step 3: Click at (x=1022, y=170)
                    print_status("Clicking at coordinates (1022, 170)...")
                    if not click_at_position(1022, 170):
                        print_error("Failed to click at coordinates (1022, 170)")
                        return False
                    
                    # Step 4: Wait 10 seconds after first click
                    print_status("Waiting 10 seconds after first click...")
                    time.sleep(10)
                    
                    # Step 5: Click at (x=356, y=356)
                    print_status("Clicking at coordinates (356, 356)...")
                    if not click_at_position(356, 356):
                        print_error("Failed to click at coordinates (356, 356)")
                        return False
                    
                    # Step 6: Wait 10 seconds after second click
                    print_status("Waiting 10 seconds after second click...")
                    time.sleep(10)
                    
                    # Step 7: Close the application
                    print_status("Closing loyalty application...")
                    close_result = close_loyalty_app()
                    if not close_result:
                        print_error("Failed to close loyalty application")
                        return False
                    
                    print_success("🎉 Mobile KYC Check automation completed successfully!")
                    
                except Exception as e:
                    print_error(f"Mobile KYC Check automation failed with error: {e}")
                    return False
                    
            else:
                print_error("❌ Cannot proceed with mobile KYC check - no device connected")
                return False
            
            # ============================================================================
            # PHASE 7: BANK VERIFICATION WEB AUTOMATION
            # ============================================================================
            print_header("PHASE 7: BANK VERIFICATION WEB AUTOMATION")
            
            # Navigate to bank master page
            print_status("Navigating to bank master page...")
            await page.goto('http://digisol.loyaltyxpert.staging/customer/bank-master/bank-details', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Bank master page loaded")
            
            # Verify we've navigated to the correct bank master page
            current_url = page.url
            if 'bank-master' in current_url:
                print_success("Successfully navigated to bank master page")
                print(f"Current URL: {current_url}")
            else:
                print_error("Navigation to bank master page failed")
                return False
            
            # Wait for page to fully load
            await page.wait_for_timeout(3000)
            
            # Click "ADD NEW" button
            print_status("Looking for ADD NEW button...")
            add_new_selectors = [
                'button:has-text("ADD NEW")', 'a:has-text("ADD NEW")', '.btn:has-text("ADD NEW")',
                '[data-testid="add-new"]', '.add-new-btn', 'button[title*="ADD NEW" i]',
                'a[title*="ADD NEW" i]', '.btn-primary:has-text("ADD NEW")'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("ADD NEW button clicked")
            
            # Wait for form to load and ensure it's fully rendered
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Click on Customer Member ID dropdown
            print_status("Clicking on Customer Member ID dropdown...")
            member_id_selectors = [
                '#select2-bankmaster-cust_member_id-container',
                '.select2-selection__rendered[id*="cust_member_id"]',
                'span[role="textbox"][id*="cust_member_id"]'
            ]
            
            member_id_dropdown = None
            for selector in member_id_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    member_id_dropdown = await page.query_selector(selector)
                    if member_id_dropdown:
                        break
                except:
                    continue
            
            if not member_id_dropdown:
                print_error("Customer Member ID dropdown not found")
                return False
            
            await member_id_dropdown.click()
            print_success("Customer Member ID dropdown clicked")
            
            # Type unique name in the search field
            print_status(f"Typing unique name '{unique_name}' in search field...")
            search_selectors = [
                '.select2-search__field',
                'input[type="search"]',
                '.select2-search input'
            ]
            
            search_field = None
            for selector in search_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    search_field = await page.query_selector(selector)
                    if search_field:
                        break
                except:
                    continue
            
            if not search_field:
                print_error("Search field not found")
                return False
            
            await search_field.fill(unique_name)
            print_success(f"'{unique_name}' typed in search field")
            
            # Wait 2 seconds
            await page.wait_for_timeout(2000)
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Press Tab
            await page.keyboard.press('Tab')
            print_success("Tab key pressed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Type "Primary"
            print_status("Typing 'Primary'...")
            await page.keyboard.type('Primary')
            print_success("'Primary' typed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Press Tab
            await page.keyboard.press('Tab')
            print_success("Tab key pressed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Type "UPI"
            print_status("Typing 'UPI'...")
            await page.keyboard.type('UPI')
            print_success("'UPI' typed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Press Tab
            await page.keyboard.press('Tab')
            print_success("Tab key pressed")
            
            # Type unique UPI ID with unique mobile number
            print_status("Typing unique UPI ID...")
            unique_upi_mobile = generate_unique_mobile_number()
            unique_upi_id = f"{unique_upi_mobile}@ybl"
            await page.keyboard.type(unique_upi_id)
            print_success(f"'{unique_upi_id}' typed")
            
            # Press Tab
            await page.keyboard.press('Tab')
            print_success("Tab key pressed")
            
            # Handle file upload field
            print_status("Looking for file upload field...")
            file_upload_selectors = [
                'input[type="file"]', 'input[accept*="image"]', 'input[accept*="file"]',
                '#file-upload', '.file-upload', 'input[name*="file"]', 'input[name*="image"]'
            ]
            
            file_upload_field = None
            for selector in file_upload_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    file_upload_field = await page.query_selector(selector)
                    if file_upload_field:
                        break
                except:
                    continue
            
            if file_upload_field:
                print_status("File upload field found, uploading sample image...")
                # Create a sample image file if it doesn't exist
                sample_image_path = "sample_image.png"
                if not os.path.exists(sample_image_path):
                    try:
                        # Try to create a simple 1x1 pixel PNG image using PIL
                        img = Image.new('RGB', (1, 1), color='white')
                        img.save(sample_image_path)
                        print_success("Sample image created using PIL")
                    except:
                        # Fallback: create a simple text file
                        with open(sample_image_path, 'w') as f:
                            f.write("Sample file for upload")
                        print_success("Sample file created as fallback")
                
                # Upload the file
                await file_upload_field.set_input_files(sample_image_path)
                print_success("File uploaded successfully")
            else:
                print_warning("File upload field not found, continuing with keyboard navigation...")
                # Press Enter to select one image
                print_status("Pressing Enter to select image...")
                await page.keyboard.press('Enter')
                print_success("Enter key pressed for image selection")
            
            # Press Tab
            await page.keyboard.press('Tab')
            print_success("Tab key pressed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Type "Approved"
            print_status("Typing 'Approved'...")
            await page.keyboard.type('Approved')
            print_success("'Approved' typed")
            
            # Press Enter
            await page.keyboard.press('Enter')
            print_success("Enter key pressed")
            
            # Click Create Button
            print_status("Looking for Create button...")
            create_selectors = [
                'button:has-text("Create")', 'input[type="submit"]:has-text("Create")',
                '.btn:has-text("Create")', '#create-btn', '.create-btn',
                'button[title*="Create" i]', '.btn-primary:has-text("Create")'
            ]
            
            create_button = None
            for selector in create_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    create_button = await page.query_selector(selector)
                    if create_button:
                        break
                except:
                    continue
            
            if not create_button:
                print_error("Create button not found")
                return False
            
            await create_button.click()
            print_success("Create button clicked")
            
            # Wait for submission to complete
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            print_success("Bank verification form submitted successfully!")
            
            # Take a screenshot for verification
            screenshot_path = f"bank_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_path)
            print_success(f"Screenshot saved: {screenshot_path}")
            
            # ============================================================================
            # PHASE 8: FINAL MOBILE KYC CHECK AUTOMATION
            # ============================================================================
            print_header("PHASE 8: FINAL MOBILE KYC CHECK AUTOMATION")
            
            # Setup Android environment
            setup_android_environment()
            
            # Check device connection
            if check_device():
                print_status("Starting Final Mobile KYC Check Automation...")
                
                try:
                    # Step 1: Launch loyalty application
                    print_status("Launching loyalty application...")
                    launch_result = launch_loyalty_app()
                    if not launch_result:
                        print_error("Failed to launch loyalty application")
                        return False
                    
                    # Step 2: Wait 10 seconds after launch
                    print_status("Waiting 10 seconds after launch...")
                    time.sleep(10)
                    
                    # Step 3: Click at (x=1022, y=170)
                    print_status("Clicking at coordinates (1022, 170)...")
                    if not click_at_position(872, 1843):
                        print_error("Failed to click at coordinates (1022, 170)")
                        return False
                    
                    # Step 4: Wait 10 seconds after first click
                    print_status("Waiting 10 seconds after first click...")
                    time.sleep(10)
                    
                    # Step 5: Click at (x=356, y=356)
                    print_status("Clicking at coordinates (356, 356)...")
                    if not click_at_position(538, 356):
                        print_error("Failed to click at coordinates (356, 356)")
                        return False
                    
                    # Step 6: Wait 10 seconds after second click
                    print_status("Waiting 10 seconds after second click...")
                    time.sleep(10)
                    
                    # Step 7: Close the application
                    print_status("Closing loyalty application...")
                    close_result = close_loyalty_app()
                    if not close_result:
                        print_error("Failed to close loyalty application")
                        return False
                    
                    print_success("🎉 Final Mobile KYC Check automation completed successfully!")
                    
                except Exception as e:
                    print_error(f"Final Mobile KYC Check automation failed with error: {e}")
                    return False
                    
            else:
                print_error("❌ Cannot proceed with final mobile KYC check - no device connected")
                return False
            
            # ============================================================================
            # COMPLETION SUMMARY
            # ============================================================================
            print_header("COMPLETION SUMMARY")
            print("=" * 80)
            print_success("🎉 Customer Group + Loyalty Configuration + Customer Creation + KYC + Mobile KYC Check + Bank Verification + Final Mobile KYC Check automation completed successfully!")
            print("✅ Customer Group Operations: COMPLETED")
            print("✅ Loyalty Configuration Operations: COMPLETED")
            print("✅ Customer Creation Operations: COMPLETED")
            print("✅ KYC Web Operations: COMPLETED (Form submitted)")
            print("✅ Mobile KYC Check Operations: COMPLETED")
            print("✅ Bank Verification Operations: COMPLETED")
            print("✅ Final Mobile KYC Check Operations: COMPLETED")
            print("=" * 80)
            
            return True
            
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")
        return False
    
    # Note: Browser will be kept open for mobile automation
    print_status("Web automation completed, keeping browser open for mobile automation...")

# ============================================================================
# MOBILE AUTOMATION FUNCTIONS (from New_Customer_Login.py)
# ============================================================================

def setup_android_environment():
    """Setup Android environment"""
    android_home = "/home/ansh/Android/Sdk"
    os.environ['ANDROID_HOME'] = android_home
    os.environ['PATH'] = f"{android_home}/platform-tools:{android_home}/emulator:{os.environ.get('PATH', '')}"

def check_device():
    """Check if device is connected"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.strip().split('\n')[1:]
        connected_devices = [d for d in devices if d.strip() and 'device' in d]
        
        if connected_devices:
            print(f"✅ Device connected: {connected_devices[0]}")
            return True
        else:
            print("❌ No device connected")
            return False
    except Exception as e:
        print(f"❌ Error checking device: {e}")
        return False

def launch_loyalty_app():
    """Launch LoyaltyXpert app"""
    print("🚀 Launching LoyaltyXpert app...")
    try:
        # Force stop first
        subprocess.run(['adb', 'shell', 'am', 'force-stop', 'ecosmob.loyaltyxpert.com'], check=True)
        time.sleep(2)
        
        # Launch app
        subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'ecosmob.loyaltyxpert.com/.MainActivity'], check=True)
        time.sleep(20)  # Wait 20 seconds for app to fully load
        print("✅ App launched successfully!")
        return True
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return False

def close_loyalty_app():
    """Close the loyalty application"""
    print("🔒 Closing LoyaltyXpert app...")
    try:
        subprocess.run(['adb', 'shell', 'am', 'force-stop', 'ecosmob.loyaltyxpert.com'], check=True)
        time.sleep(2)
        print("✅ App closed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error closing app: {e}")
        return False

def click_at_position(x, y, description=""):
    """Click at specific coordinates"""
    try:
        print(f"📱 Clicking at position ({x}, {y}): {description}")
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)], check=True)
        time.sleep(1)
        print(f"✅ Click executed at ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error clicking at ({x}, {y}): {e}")
        return False

def clear_input_field():
    """Clear input field"""
    print("🧹 Clearing input field...")
    try:
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'], check=True)
        time.sleep(0.5)
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_DEL'], check=True)
        time.sleep(1)
        print("✅ Input field cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing input field: {e}")
        return False

def enter_phone_number(unique_mobile_number):
    """Enter phone number using the unique mobile number from web automation"""
    # Remove timestamp suffix if present to get clean 10-digit number
    clean_phone = unique_mobile_number.split('_')[0] if '_' in unique_mobile_number else unique_mobile_number
    
    print(f"📞 Entering unique phone number: {clean_phone}")
    
    # Click phone number field
    if click_at_position(331, 1672, "Phone number field"):
        clear_input_field()
        time.sleep(2)
        
        # Enter phone number
        subprocess.run(['adb', 'shell', 'input', 'text', clean_phone])
        time.sleep(2)
        print("✅ Unique phone number entered!")
        return True
    return False

def press_enter_key():
    """Press Enter key to submit the phone number"""
    print("↵ Pressing Enter key...")
    try:
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], check=True)
        time.sleep(2)
        print("✅ Enter key pressed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error pressing Enter key: {e}")
        return False

def get_ui_dump():
    """Get UI dump using uiautomator"""
    try:
        print("🔍 Getting UI dump...")
        result = subprocess.run(['adb', 'shell', 'uiautomator', 'dump'], capture_output=True, text=True)
        if result.returncode == 0:
            # Pull the UI dump file
            subprocess.run(['adb', 'pull', '/sdcard/window_dump.xml', 'ui_dump.xml'], check=True)
            print("✅ UI dump saved as ui_dump.xml")
            
            # Read and parse the UI dump
            with open('ui_dump.xml', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text from UI dump
            text_elements = re.findall(r'text="([^"]*)"', content)
            desc_elements = re.findall(r'content-desc="([^"]*)"', content)
            
            all_text = text_elements + desc_elements
            combined_text = '\n'.join([text for text in all_text if text.strip()])
            
            print(f"📝 Extracted {len(all_text)} text elements from UI dump")
            return combined_text
        else:
            print("❌ Failed to get UI dump")
            return None
    except Exception as e:
        print(f"❌ Error getting UI dump: {e}")
        return None

def find_otp_in_text(text, method_name=""):
    """Find OTP in text using comprehensive regex patterns"""
    if not text:
        print(f"❌ No text to search in {method_name}")
        return None
    
    print(f"🔍 Searching for OTP in {method_name}...")
    
    # Print first 200 characters for debugging
    preview = text[:200].replace('\n', ' ').strip()
    print(f"📝 Text preview: {preview}...")
    
    # Comprehensive OTP patterns (in order of preference)
    otp_patterns = [
        # Specific OTP patterns
        r'OTP[:\s]*(\d{4,6})',                    # OTP: 123456
        r'verification[:\s]*(\d{4,6})',           # verification: 123456
        r'code[:\s]*(\d{4,6})',                   # code: 123456
        r'pin[:\s]*(\d{4,6})',                    # pin: 123456
        r'password[:\s]*(\d{4,6})',               # password: 123456
        
        # Common phrases with OTP
        r'please submit this\s*(\d{4,6})',        # please submit this 123456
        r'enter\s*(\d{4,6})',                     # enter 123456
        r'use\s*(\d{4,6})',                       # use 123456
        r'type\s*(\d{4,6})',                      # type 123456
        
        # Generic patterns
        r'(\d{4,6})',                             # Any 4-6 digit number
        r'(\d{4})',                               # Any 4 digit number
        r'(\d{6})',                               # Any 6 digit number
    ]
    
    for pattern in otp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Filter out common non-OTP numbers
            for match in matches:
                if not is_common_non_otp_number(match):
                    print(f"✅ Found potential OTP: {match} (pattern {otp_patterns.index(pattern) + 1})")
                    return match
    
    print("❌ No OTP found in text")
    return None

def is_common_non_otp_number(number):
    """Check if number is likely not an OTP"""
    common_non_otp = [
        '0000', '1111', '1234', '12345', '123456',  # Sequential
        '9999', '8888', '7777', '6666', '5555',      # Repeated
        '000000', '111111', '222222', '333333',       # Long repeated
        '0123', '01234', '012345', '0123456',         # Zero-prefixed sequential
    ]
    return number in common_non_otp

def input_text_at_coordinates(text, x, y, description=""):
    """Input text at specific coordinates"""
    try:
        print(f"📝 Inputting text '{text}' at ({x}, {y}): {description}")
        
        # Click at the position
        if not click_at_position(x, y, description):
            return False
        
        # Clear any existing text
        clear_input_field()
        
        # Input the text
        subprocess.run(['adb', 'shell', 'input', 'text', text], check=True)
        time.sleep(2)
        
        print(f"✅ Text '{text}' input successfully at ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error inputting text at ({x}, {y}): {e}")
        return False

def monitor_for_otp(max_attempts=10, delay=3):
    """Monitor for OTP arrival with multiple attempts"""
    print(f"🔍 Monitoring for OTP (max {max_attempts} attempts, {delay}s delay)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        print("=" * 40)
        
        # Method 1: UI Dump
        ui_text = get_ui_dump()
        if ui_text:
            otp = find_otp_in_text(ui_text, "UI Dump")
            if otp:
                return otp
        
        if attempt < max_attempts:
            print(f"⏳ Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("❌ OTP not found after all attempts")
    return None

def extract_and_fill_otp():
    """Extract OTP and fill it in input field"""
    print("\n🎯 OTP EXTRACTION AND FILLING PROCESS")
    print("=" * 60)
    
    # Step 1: Monitor for OTP arrival
    print("\n🔍 STEP 1: Monitoring for OTP arrival...")
    otp = monitor_for_otp(max_attempts=15, delay=2)
    
    if not otp:
        print("❌ No OTP found after monitoring")
        return False
    
    # Step 2: Fill OTP in input field
    print(f"\n📝 STEP 2: Filling OTP '{otp}' in input field...")
    target_x, target_y = 157, 1851  # OTP input field coordinates
    
    if input_text_at_coordinates(otp, target_x, target_y, "OTP input field"):
        print(f"✅ OTP '{otp}' successfully filled in input field!")
        
        # Step 3: Press Enter to submit
        print("\n↵ STEP 3: Pressing Enter to submit OTP...")
        try:
            subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], check=True)
            time.sleep(2)
            print("✅ Enter key pressed successfully!")
        except Exception as e:
            print(f"❌ Error pressing Enter: {e}")
        
        return True
    else:
        print(f"❌ Failed to fill OTP '{otp}' in input field")
        return False

def run_mobile_automation(unique_mobile_number):
    """Run mobile automation with OTP capture using unique mobile number"""
    print_header("Starting Mobile Automation with OTP Capture")
    
    # Step 1: Launch app
    print_status("Step 1: Launching LoyaltyXpert app...")
    if not launch_loyalty_app():
        print_error("App launch failed")
        return False
    
    time.sleep(3)
    
    # Step 2: Enter phone number
    print_status("Step 2: Entering unique phone number...")
    if not enter_phone_number(unique_mobile_number):
        print_error("Phone number input failed")
        return False
    
    time.sleep(2)
    
    # Step 3: Click login button
    print_status("Step 3: Clicking login button...")
    if not click_at_position(530, 1282, "Login button"):
        print_error("Login button click failed")
        return False
    
    time.sleep(3)
    
    # Step 4: Extract and fill OTP
    print_status("Step 4: Extracting and filling OTP...")
    if not extract_and_fill_otp():
        print_error("OTP extraction and filling failed")
        return False
    
    # Step 5: Wait 5 seconds after OTP submission
    print_status("Step 5: Waiting 5 seconds after OTP submission...")
    time.sleep(5)
    print_success("Waited 5 seconds after OTP submission")
    
    print_success("Mobile automation with OTP capture completed")
    return True

# ============================================================================
# KYC WEB AUTOMATION FUNCTIONS (from KYC_WEB.py)
# ============================================================================

async def run_kyc_web_automation():
    """Run KYC web automation using Playwright"""
    print_header("Starting KYC Web Automation")
    
    try:
        # Navigate to Customer KYC page
        print_status("Navigating to Customer KYC page...")
        await page.goto('http://digisol.loyaltyxpert.staging/customer/customer-kyc/index', 
                       wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_load_state('domcontentloaded')
        print_success("Customer KYC page loaded")
        
        # Click ADD NEW button
        print_status("Looking for ADD NEW button...")
        add_new_selectors = [
            'button:has-text("ADD NEW")', 'button:has-text("Add New")', 'button:has-text("Add")',
            'a:has-text("ADD NEW")', 'a:has-text("Add New")', 'a:has-text("Add")',
            '.btn-primary:has-text("ADD NEW")', '.btn-success:has-text("ADD NEW")',
            'input[value="ADD NEW"]', 'input[value="Add New"]'
        ]
        
        add_new_button = None
        for selector in add_new_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                add_new_button = await page.query_selector(selector)
                if add_new_button:
                    break
            except:
                continue
        
        if not add_new_button:
            print_error("ADD NEW button not found")
            return False
        
        await add_new_button.click()
        print_success("ADD NEW button clicked")
        
        # Wait for form to load
        await page.wait_for_timeout(2000)
        
        # Select Customer Member dropdown
        print_status("Selecting Customer Member dropdown...")
        customer_member_selectors = [
            '#select2-customer_member-container', 
            'span[title="Select"]',
            '.select2-selection__rendered[title="Select"]',
            'span.select2-selection__rendered',
            'div[role="combobox"]',
            'select[name*="customer_member"]',
            'select[id*="customer_member"]'
        ]
        
        customer_member_dropdown = None
        for selector in customer_member_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                customer_member_dropdown = await page.query_selector(selector)
                if customer_member_dropdown:
                    break
            except:
                continue
        
        if not customer_member_dropdown:
            print_error("Customer Member dropdown not found")
            return False
        
        await customer_member_dropdown.click()
        print_success("Customer Member dropdown clicked")
        
        # Wait for dropdown to open and type unique name
        await page.wait_for_timeout(1000)
        await page.keyboard.type(unique_name)
        # Wait 2 seconds after typing before pressing Enter
        await page.wait_for_timeout(2000)
        await page.keyboard.press('Enter')
        print_success(f"Customer Member '{unique_name}' selected")
        
        # Wait for selection to be applied
        await page.wait_for_timeout(2000)
        
        # Select KYC Document Type dropdown
        print_status("Selecting KYC Document Type dropdown...")
        kyc_doc_type_selectors = [
            '#select2-kyc_doc_type-container', 
            'span[title="Select Type"]',
            '.select2-selection__rendered[title="Select Type"]',
            'span.select2-selection__rendered',
            'div[role="combobox"]',
            'select[name*="kyc_doc_type"]',
            'select[id*="kyc_doc_type"]',
            'input[placeholder*="Select Type"]',
            'input[placeholder*="Document Type"]'
        ]
        
        kyc_doc_type_dropdown = None
        for selector in kyc_doc_type_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                kyc_doc_type_dropdown = await page.query_selector(selector)
                if kyc_doc_type_dropdown:
                    print_success(f"Found KYC Document Type dropdown with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if not kyc_doc_type_dropdown:
            print_error("KYC Document Type dropdown not found with any selector")
            return False
        
        await kyc_doc_type_dropdown.click()
        print_success("KYC Document Type dropdown clicked")
        
        # Wait for dropdown to open and select "PAN CARD"
        await page.wait_for_timeout(1000)
        await page.keyboard.type('PAN CARD')
        await page.keyboard.press('Enter')
        print_success("KYC Document Type 'PAN CARD' selected")
        
        # Wait for selection to be applied
        await page.wait_for_timeout(2000)
        
        # Press Tab to move to next field
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(500)
        
        # Type PAN number "MBGPK6487E"
        await page.keyboard.type('MBGPK6487E')
        print_success("PAN number 'MBGPK6487E' entered")
        
        # Press Tab only after PAN number entry
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(300)
        print_success("Tab pressed after PAN number entry")
        
        # After Tab, handle file upload for image/document
        print_status("Handling file upload after Tab key...")
        
        # Look for file input field
        file_input_selectors = [
            'input[type="file"]', 'input[accept*="image"]', 'input[accept*=".png"]',
            'input[accept*=".jpg"]', 'input[accept*=".jpeg"]', 'input[accept*=".pdf"]',
            'input[name*="file"]', 'input[name*="document"]', 'input[name*="image"]',
            'input[id*="file"]', 'input[id*="document"]', 'input[id*="image"]'
        ]
        
        file_input = None
        for selector in file_input_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                file_input = await page.query_selector(selector)
                if file_input:
                    print_success(f"Found file input with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if file_input:
            # Create a sample image file for upload
            print_status("Creating sample image file for upload...")
            try:
                # Create a simple sample image
                sample_image_path = "sample_image.png"
                
                # Try to create a sample image using PIL, fallback to basic file creation
                try:
                    from PIL import Image, ImageDraw
                    # Create a simple image
                    img = Image.new('RGB', (100, 100), color='red')
                    draw = ImageDraw.Draw(img)
                    draw.text((10, 40), 'Sample', fill='white')
                    img.save(sample_image_path)
                    print_success(f"Created sample image: {sample_image_path}")
                except ImportError:
                    # Fallback: create a basic file
                    with open(sample_image_path, 'w') as f:
                        f.write("Sample image content")
                    print_success(f"Created basic sample file: {sample_image_path}")
                
                # Upload the file
                await file_input.set_input_files(sample_image_path)
                print_success(f"File uploaded successfully: {sample_image_path}")
                
                # Wait for upload to complete
                await page.wait_for_timeout(2000)
                
            except Exception as e:
                print_error(f"File upload failed: {e}")
                return False
        else:
            print_error("File input field not found")
            return False
        
        print_success("File upload completed successfully")
        
        # Click Add button to submit the form
        print_status("Looking for Add button to submit form...")
        add_button_selectors = [
            'button:has-text("Add")', 'button:has-text("Save")', 'button:has-text("Submit")',
            'input[type="submit"][value*="Add" i]', 'input[type="submit"][value*="Save" i]',
            '.btn-primary:has-text("Add")', '.btn-success:has-text("Add")',
            'button[type="submit"]', 'input[type="submit"]'
        ]
        
        add_button = None
        for selector in add_button_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                add_button = await page.query_selector(selector)
                if add_button:
                    print_success(f"Found Add button with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if not add_button:
            print_error("Add button not found")
            return False
        
        # Click the Add button
        await add_button.click()
        print_success("Add button clicked successfully")
        
        # Wait 10 seconds after clicking Add button
        print_status("Waiting 10 seconds after form submission...")
        await page.wait_for_timeout(10000)
        print_success("Waited 10 seconds after form submission")
        
        # Select KYC Status dropdown and set to "rejected"
        print_status("Looking for KYC Status dropdown...")
        kyc_status_selectors = [
            'select[name="kyc_status"]', 'select.kyc-status-dropdown',
            'select[data-id="3650"]', 'select[name*="kyc_status"]'
        ]
        
        kyc_status_dropdown = None
        for selector in kyc_status_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                kyc_status_dropdown = await page.query_selector(selector)
                if kyc_status_dropdown:
                    print_success(f"Found KYC Status dropdown with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if not kyc_status_dropdown:
            print_error("KYC Status dropdown not found")
            return False
        
        # Select "rejected" option
        await kyc_status_dropdown.select_option(value="rejected")
        print_success("KYC Status set to 'rejected'")
        
        # Wait 2 seconds after status selection
        await page.wait_for_timeout(2000)
        print_success("Waited 2 seconds after status selection")
        
        # Find and fill the remarks textarea
        print_status("Looking for remarks textarea...")
        remarks_selectors = [
            '#customerkyc-kyc_verify_note', 'textarea[name="CustomerKyc[kyc_verify_note]"]',
            'textarea[placeholder="Remarks"]', 'textarea[id*="kyc_verify_note"]'
        ]
        
        remarks_textarea = None
        for selector in remarks_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                remarks_textarea = await page.query_selector(selector)
                if remarks_textarea:
                    print_success(f"Found remarks textarea with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if not remarks_textarea:
            print_error("Remarks textarea not found")
            return False
        
        # Fill the remarks textarea
        await remarks_textarea.click()
        await remarks_textarea.fill('For_Testin')
        print_success("Remarks filled with 'For_Testin'")
        
        # Click Save button
        print_status("Looking for Save button...")
        save_button_selectors = [
            'button:has-text("Save")', 'button:has-text("Update")', 'button:has-text("Submit")',
            'input[type="submit"][value*="Save" i]', 'input[type="submit"][value*="Update" i]',
            '.btn-primary:has-text("Save")', '.btn-success:has-text("Save")',
            'button[type="submit"]', 'input[type="submit"]'
        ]
        
        save_button = None
        for selector in save_button_selectors:
            try:
                await page.wait_for_selector(selector, state='visible', timeout=2000)
                save_button = await page.query_selector(selector)
                if save_button:
                    print_success(f"Found Save button with selector: {selector}")
                    break
            except Exception as e:
                print_warning(f"Selector {selector} failed: {e}")
                continue
        
        if not save_button:
            print_error("Save button not found")
            return False
        
        # Click the Save button
        await save_button.click()
        print_success("Save button clicked successfully")
        
        # Wait 2 seconds after clicking Save button
        print_status("Waiting 2 seconds after Save button click...")
        await page.wait_for_timeout(2000)
        print_success("Waited 2 seconds after Save button click")
        
        print_success("KYC Web automation completed")
        return True
        
    except Exception as e:
        print_error(f"KYC web automation error: {e}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function to run the automation"""
    print_header("CUSTOMER GROUP + LOYALTY CONFIGURATION + CUSTOMER CREATION + MOBILE AUTOMATION + KYC WEB AUTOMATION")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Phase 1: Customer Group Operations (Login → Search → ADD NEW → Fill Form → Submit)")
    print("2. Phase 2: Loyalty Configuration Operations (Navigate → ADD NEW → Fill Form → Create)")
    print("3. Phase 3: Customer Creation Operations (Navigate → ADD NEW → Fill Form → Submit)")
    print("4. Phase 4: Mobile Automation (App Launch → Login → OTP Capture → Wait)")
    print("5. Phase 5: KYC Web Automation (Navigate → ADD NEW → Fill KYC Details → Submit Form)")
    print("6. Phase 6: Mobile KYC Check Automation (App Launch → Wait → Click (1022,170) → Wait → Click (356,356) → Wait → Close App)")
    print("7. Phase 7: Bank Verification Web Automation (Navigate → ADD NEW → Fill Bank Details → Submit)")
    print("8. Phase 8: Final Mobile KYC Check Automation (App Launch → Wait → Click (1022,170) → Wait → Click (356,356) → Wait → Close App)")
    print("=" * 80)
    
    # Create logs directory if it doesn't exist
    os.makedirs('customer_group_loyalty_config_logs', exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"customer_group_loyalty_config_logs/customer_group_loyalty_config_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_filename}")
    
    # Redirect output to log file
    with open(log_filename, 'w') as log_file:
        # Run the web automation
        print_header("PHASE 1: WEB AUTOMATION")
        web_success = await run_web_automation()
        
        if web_success:
            print_success("🎉 Web automation (including Mobile + KYC) completed successfully!")
        else:
            print_error("❌ Web automation failed")
        
        # Final summary
        print_header("FINAL SUMMARY")
        print("=" * 80)
        if web_success:
            print_success("🎉 All operations completed successfully!")
            print("✅ Customer Group Operations: COMPLETED")
            print("✅ Loyalty Configuration Operations: COMPLETED")
            print("✅ Customer Creation Operations: COMPLETED")
            print("✅ Mobile Automation: COMPLETED")
            print("✅ KYC Web Operations: COMPLETED")
            print("✅ Mobile KYC Check Operations: COMPLETED")
            print("✅ Bank Verification Operations: COMPLETED")
            print("✅ Final Mobile KYC Check Operations: COMPLETED")
        else:
            print_error("❌ Automation failed")
    
    print("=" * 80)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import playwright
    except ImportError:
        print_error("Playwright not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    
    # Run the automation
    asyncio.run(main())
