#!/usr/bin/env python3
"""
Customer_Create.py
Web Automation for Customer Creation
Complete workflow: Login → Navigate to Customer Master → ADD NEW → Fill Customer Details → Submit
"""

import asyncio
import os
import sys
import subprocess
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

# ============================================================================
# WEB AUTOMATION FUNCTIONS
# ============================================================================

async def run_web_automation():
    """Run web automation using Playwright"""
    print_header("Starting Customer Creation Web Automation")
    
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
            await mobile_field.fill('1112223334')
            print_success("Customer Mobile Number filled with '1112223334'")
            
            # Use Tab navigation to move to next fields
            print_status("Using Tab navigation to fill remaining fields...")
            
            # Press Tab to move to next field and type "Eco_User"
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('Eco_User')
            print_success("Customer Name field filled with 'Eco_User'")
            
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
            
            # Wait for dropdown to open and type "EcoQA"
            await page.wait_for_timeout(1000)
            await page.keyboard.type('EcoQA')
            await page.keyboard.press('Enter')
            print_success("Customer Group 'EcoQA' selected")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Press Tab 3 times to move to next fields
            for i in range(3):
                await page.keyboard.press('Tab')
                await page.wait_for_timeout(300)
            
            # Type "7426972890"
            await page.keyboard.type('7426972890')
            print_success("Additional phone field filled with '7426972890'")
            
            # Press Tab to move to address field
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            await page.keyboard.type('Ahmedabad India')
            print_success("Address field filled with 'Ahmedabad India'")
            
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
            
            print_success("Customer Creation web automation completed")
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
    print_header("CUSTOMER CREATION WEB AUTOMATION")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Web Automation: Login → Navigate to Customer Master")
    print("2. Form Filling: ADD NEW → Fill Customer Details")
    print("3. Customer Information: Mobile, Name, Company, Group")
    print("4. Additional Details: Phone, Address, Aadhaar/PAN Status")
    print("5. Form Submission: Click Add Button")
    print("=" * 80)
    
    # Create logs directory
    os.makedirs('customer_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"customer_logs/customer_creation_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_file}")
    
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
        print_success("🎉 Customer Creation automation completed successfully!")
        print("✅ Web Automation: COMPLETED")
        print("✅ Login: COMPLETED")
        print("✅ Navigation to Customer Master: COMPLETED")
        print("✅ ADD NEW Button: COMPLETED")
        print("✅ Customer Mobile Number: COMPLETED")
        print("✅ Customer Name: COMPLETED")
        print("✅ Company: COMPLETED")
        print("✅ Customer Group Selection: COMPLETED")
        print("✅ Additional Phone: COMPLETED")
        print("✅ Address: COMPLETED")
        print("✅ Aadhaar/PAN Status: COMPLETED")
        print("✅ Add Button: COMPLETED")
    else:
        print_error("❌ Customer Creation automation failed")
    
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
