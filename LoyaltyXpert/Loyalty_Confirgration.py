#!/usr/bin/env python3
"""
Loyalty_Confirgration.py
Web Automation for Loyalty Configuration Groups
Complete workflow: Login → Navigate to Configuration Groups → ADD NEW → Fill Group Name
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
    print_header("Starting Loyalty Configuration Web Automation")
    
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
            await group_name_field.fill('EcoQA')
            print_success("Configuration Group Name filled with 'EcoQA'")
            
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
                '#select2-configurationgroups-grp_cust_category_id-container', 
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
            
            # Wait for dropdown to open and type "EcoAQ"
            await page.wait_for_timeout(1000)
            await page.keyboard.type('EcoAQ')
            await page.keyboard.press('Enter')
            print_success("Customer Group 'EcoAQ' selected")
            
            # Wait for selection to be applied
            await page.wait_for_timeout(2000)
            
            # Press Tab to move to Create button
            await page.keyboard.press('Tab')
            await page.wait_for_timeout(500)
            
            # Click Create button
            print_status("Looking for Create button...")
            create_selectors = [
                'button:has-text("Create")', 'button:has-text("Save")', 'button:has-text("Submit")',
                'input[type="submit"][value*="Create" i]', 'input[type="submit"][value*="Save" i]',
                '.btn-primary:has-text("Create")', '.btn-success:has-text("Create")',
                'button[type="submit"]', 'input[type="submit"]'
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
            
            # Wait for form submission
            await page.wait_for_timeout(3000)
            
            print_success("Loyalty Configuration web automation completed")
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
    print_header("LOYALTY CONFIGURATION WEB AUTOMATION")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Web Automation: Login → Navigate to Configuration Groups")
    print("2. Form Filling: ADD NEW → Fill Configuration Group Name 'EcoQA'")
    print("3. Additional Fields: Description, Redemption Target, Loyalty Rate")
    print("4. Customer Group Selection: Dropdown → Type 'EcoAQ' → Enter")
    print("5. Form Submission: Click Create Button")
    print("=" * 80)
    
    # Create logs directory
    os.makedirs('loyalty_config_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"loyalty_config_logs/loyalty_config_attempt_{timestamp}.log"
    
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
        print_success("🎉 Loyalty Configuration automation completed successfully!")
        print("✅ Web Automation: COMPLETED")
        print("✅ Login: COMPLETED")
        print("✅ Navigation to Configuration Groups: COMPLETED")
        print("✅ ADD NEW Button: COMPLETED")
        print("✅ Configuration Group Name: COMPLETED")
        print("✅ Description Field: COMPLETED")
        print("✅ Redemption Target Field: COMPLETED")
        print("✅ Loyalty Rate Field: COMPLETED")
        print("✅ Customer Group Selection: COMPLETED")
        print("✅ Create Button: COMPLETED")
    else:
        print_error("❌ Loyalty Configuration automation failed")
    
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
