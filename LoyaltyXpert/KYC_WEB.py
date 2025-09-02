#!/usr/bin/env python3
"""
KYC_WEB.py
Web Automation for Customer KYC (Know Your Customer) Form
Complete workflow: Login → Navigate to Customer KYC → ADD NEW → Fill KYC Details → Submit
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
    print_header("Starting KYC Web Automation")
    
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
            
            # Navigate to customer KYC page
            print_status("Navigating to customer KYC page...")
            await page.goto('http://digisol.loyaltyxpert.staging/customer/customer-kyc/index', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Customer KYC page loaded")
            
            # Verify we've navigated to the correct customer KYC page
            current_url = page.url
            if 'customer-kyc' in current_url:
                print_success("Successfully navigated to customer KYC page")
                print(f"Current URL: {current_url}")
            else:
                print_error("Navigation to customer KYC page failed")
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
            
            # Select Customer Member from dropdown
            print_status("Selecting Customer Member from dropdown...")
            customer_member_selectors = [
                '#select2-customerkyc-cust_member_id-container', 
                'span[role="textbox"][aria-readonly="true"]',
                '.select2-selection__rendered[id*="cust_member_id"]'
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
            
            # Wait for dropdown to open and type "Eco_user"
            await page.wait_for_timeout(1000)
            await page.keyboard.type('Eco_user')
            # Wait 2 seconds after typing before pressing Enter
            await page.wait_for_timeout(2000)
            await page.keyboard.press('Enter')
            print_success("Customer Member 'Eco_user' selected")
            
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
                print_status("Trying to find dropdown by text content...")
                # Try to find by text content
                try:
                    dropdown_by_text = await page.query_selector('text="Select Type"')
                    if dropdown_by_text:
                        kyc_doc_type_dropdown = dropdown_by_text
                        print_success("Found dropdown by text content")
                    else:
                        print_error("Could not find KYC Document Type dropdown")
                        return False
                except:
                    print_error("Could not find KYC Document Type dropdown")
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
                # Upload a sample PNG image from your Pictures directory
                print_status("Uploading sample PNG image from Pictures directory...")
                try:
                    # Use a sample image from your Pictures directory
                    sample_image_path = "/home/ansh/Pictures/Screenshot from 2025-09-02 10-10-29.png"
                    
                    # Check if sample image exists
                    if os.path.exists(sample_image_path):
                        print_success(f"Found sample image: {sample_image_path}")
                    else:
                        # Try alternative paths
                        alternative_paths = [
                            "/home/ansh/Pictures/Screenshot from 2025-09-01 17-50-23.png",
                            "/home/ansh/Pictures/Screenshot from 2025-08-29 15-30-45.png",
                            "/home/ansh/Pictures/Screenshot from 2025-08-28 10-15-22.png"
                        ]
                        
                        sample_image_path = None
                        for path in alternative_paths:
                            if os.path.exists(path):
                                sample_image_path = path
                                print_success(f"Found alternative image: {sample_image_path}")
                                break
                        
                        if not sample_image_path:
                            print_warning("No sample images found in Pictures directory")
                            print_status("Please place a PNG image in your Pictures directory for upload")
                            return False
                    
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
            print_error(f"Web automation error: {e}")
            return False
        finally:
            await browser.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function"""
    print_header("CUSTOMER KYC WEB AUTOMATION")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Web Automation: Login → Navigate to Customer KYC")
    print("2. Form Filling: ADD NEW → Fill KYC Details")
    print("3. Customer Selection: Dropdown → Type 'Eco_user' → Enter")
    print("4. Document Type: Dropdown → Select 'PAN CARD'")
    print("5. PAN Details: Enter 'MBGPK6487E' → Tab → File Upload → Add Button → Wait 10s")
    print("6. KYC Status: Select 'rejected' → Wait 2s → Fill Remarks → Save → Wait 2s")
    print("=" * 80)
    
    # Create logs directory
    os.makedirs('kyc_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"kyc_logs/kyc_web_attempt_{timestamp}.log"
    
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
        print_success("🎉 Customer KYC automation completed successfully!")
        print("✅ Web Automation: COMPLETED")
        print("✅ Login: COMPLETED")
        print("✅ Navigation to Customer KYC: COMPLETED")
        print("✅ ADD NEW Button: COMPLETED")
        print("✅ Customer Member Selection: COMPLETED")
        print("✅ KYC Document Type Selection: COMPLETED")
        print("✅ PAN Number Entry: COMPLETED")
        print("✅ Add Button: COMPLETED")
        print("✅ KYC Status Selection: COMPLETED")
        print("✅ Remarks Entry: COMPLETED")
        print("✅ Save Button: COMPLETED")
        print("✅ Final Wait: COMPLETED")
    else:
        print_error("❌ Customer KYC automation failed")
    
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
