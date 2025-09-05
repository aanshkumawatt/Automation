#!/usr/bin/env python2
"""
Bank_Verified_Web.py
Web Automation for Bank Verification
Complete workflow: Login → Navigate to Bank Master → ADD NEW → Fill Bank Details → Submit
"""

import asyncio
import os
import sys
import subprocess
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

# ============================================================================
# WEB AUTOMATION FUNCTIONS
# ============================================================================

async def run_web_automation():
    """Run web automation using Playwright"""
    print_header("Starting Bank Verification Web Automation")
    
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
            
            # Type "Eco_User" in the search field
            print_status("Typing 'Eco_User' in search field...")
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
            
            await search_field.fill('Eco_User')
            print_success("'Eco_User' typed in search field")
            
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
            
            # Type "7425972890@ybl"
            print_status("Typing '7425972890@ybl'...")
            await page.keyboard.type('7425972890@ybl')
            print_success("'7425972890@ybl' typed")
            
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
            
            return True
            
        except Exception as e:
            print_error(f"Automation failed with error: {e}")
            # Take error screenshot
            try:
                error_screenshot_path = f"bank_verification_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await page.screenshot(path=error_screenshot_path)
                print_status(f"Error screenshot saved: {error_screenshot_path}")
            except:
                pass
            return False
        
        finally:
            # Close browser
            await browser.close()
            print_status("Browser closed")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function to run the automation"""
    print_header("Bank Verification Web Automation")
    print("=" * 50)
    
    try:
        success = await run_web_automation()
        
        if success:
            print_success("\n🎉 Bank Verification Automation completed successfully!")
            print("Check the screenshot for verification.")
        else:
            print_fail("\n❌ Bank Verification Automation failed!")
            print("Check the error screenshot and logs for details.")
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print_warning("\n⚠️  Automation interrupted by user")
        return 1
    except Exception as e:
        print_error(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    # Run the async main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
