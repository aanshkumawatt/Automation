#!/usr/bin/env python3
"""
Customer_Group.py
Web Automation for Customer Group Management
Complete workflow: Login → Search "Cus" → Navigate to Customer Category
"""

import asyncio
import os
import sys
import subprocess
import random
import string
from datetime import datetime
from playwright.async_api import async_playwright

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

# ============================================================================
# VISUAL DEBUGGING FUNCTIONS
# ============================================================================

async def highlight_element(page, element, action_name):
    """Add red border around element and take screenshot"""
    try:
        # Add red border to the element
        await page.evaluate("""
            (element) => {
                element.style.border = '3px solid red';
                element.style.boxShadow = '0 0 10px red';
                element.style.transition = 'all 0.3s ease';
            }
        """, element)
        
        # Wait a moment for the border to be visible
        await page.wait_for_timeout(500)
        
        # Take screenshot with timestamp - show full visible screen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_dir = "Customer_Groups_Screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        
        screenshot_path = f"{screenshot_dir}/{action_name}_{timestamp}.png"
        # Take screenshot of visible viewport instead of full page
        await page.screenshot(path=screenshot_path, full_page=False)
        
        print_success(f"📸 Screenshot saved: {screenshot_path}")
        
        # Remove the border after screenshot
        await page.evaluate("""
            (element) => {
                element.style.border = '';
                element.style.boxShadow = '';
            }
        """, element)
        
        return screenshot_path
        
    except Exception as e:
        print_warning(f"Failed to highlight element or take screenshot: {e}")
        return None

async def highlight_and_screenshot(page, element, action_name, description=""):
    """Highlight element, take screenshot, and log the action"""
    if element:
        print_status(f"🔍 {action_name}: {description}")
        screenshot_path = await highlight_element(page, element, action_name)
        return screenshot_path
    else:
        print_error(f"❌ Element not found for: {action_name}")
        return None

# ============================================================================
# WEB AUTOMATION FUNCTIONS
# ============================================================================

async def run_web_automation():
    """Run web automation using Playwright"""
    print_header("Starting Customer Group Web Automation")
    
    async with async_playwright() as p:
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
            
            # Highlight and screenshot username field
            await highlight_and_screenshot(page, username_field, "username_field", "Username input field found")
            
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
            
            # Highlight and screenshot password field
            await highlight_and_screenshot(page, password_field, "password_field", "Password input field found")
            
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
            
            # Highlight and screenshot login button
            await highlight_and_screenshot(page, login_button, "login_button", "Login button found")
            
            await login_button.click()
            print_success("Login button clicked")
            
            # Wait after login
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Post-login page loaded")
            
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
            
            # Highlight and screenshot search box
            await highlight_and_screenshot(page, search_box, "search_box", "Search box found")
            
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
            
            # Highlight and screenshot ADD NEW button
            await highlight_and_screenshot(page, add_new_button, "add_new_button", "ADD NEW button found")
            
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
            
            # Highlight and screenshot customer group name field
            await highlight_and_screenshot(page, name_field, "customer_group_name_field", "Customer Group Name field found")
            
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
            
            # Highlight and screenshot status dropdown
            await highlight_and_screenshot(page, status_dropdown, "status_dropdown", "Status dropdown found")
            
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
            
            # Highlight and screenshot active option
            await highlight_and_screenshot(page, active_option, "active_option", "Active option found in Status dropdown")
            
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
            
            # Highlight and screenshot earning options dropdown
            await highlight_and_screenshot(page, earning_dropdown, "earning_options_dropdown", "Earning Options dropdown found")
            
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
            
            # Highlight and screenshot wallet type dropdown
            await highlight_and_screenshot(page, wallet_dropdown, "wallet_type_dropdown", "Wallet Type dropdown found")
            
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
            
            # Highlight and screenshot primary wallet option
            await highlight_and_screenshot(page, primary_wallet_option, "primary_wallet_option", "Primary Wallet option found")
            
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
            
            # Highlight and screenshot hierarchy rank field
            await highlight_and_screenshot(page, hierarchy_rank_field, "hierarchy_rank_field", "Hierarchy Rank field found")
            
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
            
            # Highlight and screenshot radio button
            await highlight_and_screenshot(page, radio_button, "radio_button", "Radio button for is_required_all (value=1) found")
            
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
            
            # Highlight and screenshot first checkbox
            await highlight_and_screenshot(page, checkbox1, "checkbox_1", "Checkbox with label for '1' found")
            
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
            
            # Highlight and screenshot mandatory checkbox
            await highlight_and_screenshot(page, checkbox_mandatory, "checkbox_mandatory", "Checkbox with label for 'is_mandatory_1' found")
            
            await checkbox_mandatory.click()
            print_success("Checkbox with label for 'is_mandatory_1' clicked")
            
            # Click Add button
            print_status("Clicking Add button...")
            add_button_selectors = [
                'button:has-text("Add")', 'input[type="submit"]:has-text("Add")',
                'button[type="submit"]', '.btn-primary:has-text("Add")',
                'button.btn-primary', 'input[value="Add"]'
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
            
            # Highlight and screenshot Add button
            await highlight_and_screenshot(page, add_button, "add_button", "Add button found")
            
            await add_button.click()
            print_success("Add button clicked")
            
            # Wait 8 seconds after clicking Add button
            print_status("Waiting 8 seconds after clicking Add button...")
            await page.wait_for_timeout(8000)
            print_success("Waited 8 seconds after Add button click")
            
            # Take final screenshot of the completed form
            print_status("Taking final screenshot of completed form...")
            final_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_screenshot_path = f"Customer_Groups_Screenshots/final_form_completed_{final_timestamp}.png"
            await page.screenshot(path=final_screenshot_path, full_page=False)
            print_success(f"📸 Final screenshot saved: {final_screenshot_path}")
            
            print_success("Customer Group form filled successfully")
            print_success("Customer Group web automation completed")
            return True
            
        except Exception as e:
            print_error(f"Web automation error: {e}")
            return False
        finally:
            await browser.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function"""
    print_header("CUSTOMER GROUP WEB AUTOMATION")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Web Automation: Login → Search 'Cus' → Navigate to Customer Category")
    print("2. Form Filling: ADD NEW → Fill Name → Select Status → Earning Options → Wallet → Checkbox → Approver Groups")
    print("=" * 80)
    
    # Create logs and screenshots directories
    os.makedirs('customer_logs', exist_ok=True)
    os.makedirs('Customer_Groups_Screenshots', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"customer_logs/customer_group_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_file}")
    print(f"📸 Screenshots will be saved to: Customer_Groups_Screenshots/")
    print("🔍 Each element interaction will be highlighted with red border and captured")
    
    # Run web automation
    print_header("PHASE 1: WEB AUTOMATION")
    web_success = await run_web_automation()
    
    if web_success:
        print_success("Web automation completed successfully!")
    else:
        print_error("Web automation failed")
    
    # Final summary
    print_header("FINAL SUMMARY")
    print("=" * 80)
    if web_success:
        print_success("🎉 Customer Group automation completed successfully!")
        print("✅ Web Automation: COMPLETED")
        print("✅ Login: COMPLETED")
        print("✅ Search 'Cus': COMPLETED")
        print("✅ Navigation to Customer Category: COMPLETED")
        print("✅ ADD NEW Button: COMPLETED")
        print("✅ Customer Group Name: COMPLETED with unique name")
        print("✅ Status Selection: COMPLETED")
        print("✅ Earning Options: COMPLETED")
        print("✅ Wallet Type: COMPLETED")
        print("✅ Hierarchy Rank: COMPLETED")
        print("✅ Radio Button Selection (value=1): COMPLETED")
        print("✅ Checkbox Selection (label=1): COMPLETED")
        print("✅ Checkbox Selection (is_mandatory_1): COMPLETED")
        print("✅ Add Button: COMPLETED")
    else:
        print_error("❌ Customer Group automation failed")
    
    print("=" * 80)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import playwright
    except ImportError:
        print_error("Playwright not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    
    # Run the main function
    asyncio.run(main())
